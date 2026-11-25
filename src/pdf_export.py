
from __future__ import annotations

import json
import subprocess
from datetime import datetime
import sys
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .churn_model import compute_risk_grade


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


def _fmt_cell(value: Any) -> str:
    if isinstance(value, bool) or value is None:
        return "" if value is None else str(value)
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        if pd.isna(value):
            return ""
        if value.is_integer() or abs(value) >= 1000:
            return f"{int(round(value)):,}"
        return f"{value:,.1f}"
    return str(value)


def _env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["cell"] = _fmt_cell
    return env


def _safe_int(x: Any, default: int = 0) -> int:
    try:
        if x is None or x == "":
            return default
        return int(float(x))
    except Exception:
        return default


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None or x == "":
            return default
        return float(x)
    except Exception:
        return default


def _fmt_currency(x: Any) -> str:
    return f"₩{_safe_int(x):,}"


def _fmt_krw_short(x: Any) -> str:
    v = _safe_float(x)
    if abs(v) >= 100_000_000:
        return f"₩{v / 100_000_000:,.1f}억"
    if abs(v) >= 10_000:
        return f"₩{v / 10_000:,.0f}만"
    return f"₩{int(round(v)):,}"


def _fmt_int(x: Any) -> str:
    return f"{_safe_int(x):,}"


def _fmt_pct(x: Any, digits: int = 1) -> str:
    v = _safe_float(x, 0.0)
    if abs(v) <= 1:
        v *= 100
    return f"{v:.{digits}f}%"


def _is_datetime_series(s: pd.Series) -> bool:
    return pd.api.types.is_datetime64_any_dtype(s) or pd.api.types.is_datetime64tz_dtype(s)


def _normalize_df_for_pdf(df: pd.DataFrame | None, limit: int = 30) -> pd.DataFrame:
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame()

    out = df.head(limit).copy()

    for col in out.columns:
        s = out[col]

        if pd.api.types.is_categorical_dtype(s):
            out[col] = s.astype("object")
            s = out[col]

        if _is_datetime_series(s):
            out[col] = s.astype(str)
            s = out[col]

        if pd.api.types.is_numeric_dtype(s):
            continue

        out[col] = out[col].where(pd.notna(out[col]), "")
        out[col] = out[col].astype(str)
        out[col] = out[col].replace(
            {
                "nan": "",
                "NaN": "",
                "NaT": "",
                "None": "",
                "<NA>": "",
            }
        )

    return out


def _df_records(df: pd.DataFrame | None, limit: int = 30) -> list[dict]:
    tmp = _normalize_df_for_pdf(df, limit=limit)
    if tmp.empty:
        return []
    return tmp.to_dict(orient="records")


def _select_existing_columns(df: pd.DataFrame | None, candidates: list[str], limit: int = 30) -> pd.DataFrame:
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame()

    existing = [c for c in candidates if c in df.columns]
    if not existing:
        return pd.DataFrame()

    return _normalize_df_for_pdf(df[existing], limit=limit)


def _pick_top_rows(
    df: pd.DataFrame | None,
    sort_candidates: list[str],
    limit: int = 8,
    ascending: bool = False,
) -> list[dict]:
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return []

    tmp = df.copy()

    for col in tmp.columns:
        if pd.api.types.is_categorical_dtype(tmp[col]):
            tmp[col] = tmp[col].astype("object")

    for c in sort_candidates:
        if c in tmp.columns:
            try:
                sort_series = pd.to_numeric(tmp[c], errors="coerce")
                tmp = tmp.assign(__sort_key__=sort_series)
                tmp = tmp.sort_values("__sort_key__", ascending=ascending, na_position="last")
                tmp = tmp.drop(columns=["__sort_key__"])
                break
            except Exception:
                pass

    return _df_records(tmp, limit=limit)


def _normalize_sections(selected_sections: dict | None) -> dict:
    defaults = {
        "overview": True,
        "segment": True,
        "category": True,
        "ml": True,
        "refund": True,
        "inventory": True,
    }
    if not isinstance(selected_sections, dict):
        return defaults
    defaults.update({k: bool(v) for k, v in selected_sections.items()})
    return defaults


def _negative_sales_mode_label(mode: str) -> str:
    return {
        "refund": "환불/취소 후보로 처리",
        "exclude": "분석에서 제외",
        "keep": "원본 그대로 유지",
    }.get(mode, mode or "-")


def _negative_sales_mode_desc(mode: str) -> str:
    return {
        "refund": "음수 매출은 환불/취소 후보로 간주하여 환불 분석에도 반영합니다.",
        "exclude": "음수 매출은 이상치 또는 비분석 데이터로 간주하여 현재 분석에서 제외합니다.",
        "keep": "음수 매출을 원본 그대로 유지하여 정산/오류 가능성까지 함께 해석합니다.",
    }.get(mode, "")


def _summary_lines_from_kpi(
    kpi: dict,
    top_seg: str,
    top_cat: str,
    refund_rate: float,
    protection_value: float = 0.0,
    critical_count: int = 0,
    high_risk_count: int = 0,
    top_action: str = "-",
) -> list[str]:
    lines = []
    if high_risk_count:
        lines.append(
            f"이탈 위험 고객은 {high_risk_count:,}명이며, 이 중 {critical_count:,}명은 즉시 관리가 필요합니다."
        )
    if protection_value:
        lines.append(f"이탈 위험 고객을 지키면 30일 기준 약 {_fmt_krw_short(protection_value)}의 매출을 방어할 수 있습니다.")
    if top_cat and top_cat != "-":
        lines.append(f"카테고리 중에서는 {top_cat}의 위험 점수가 가장 높아 먼저 점검이 필요합니다.")
    if top_seg and top_seg != "-":
        lines.append(f"가장 큰 고객군은 {top_seg}입니다.")
    if top_action and top_action != "-":
        lines.append(f"이탈 위험 고객에게 가장 많이 필요한 액션은 '{top_action}'입니다.")
    if refund_rate > 0:
        lines.append(f"환불률은 {refund_rate * 100:.1f}%로, 상품·배송 이슈를 함께 점검하세요.")
    return lines[:5]


def _make_bar_rows(rows: list[dict], label_key: str, value_key: str, max_items: int = 8) -> list[dict]:
    if not rows:
        return []

    temp = []
    for row in rows[:max_items]:
        label = str(row.get(label_key, "-"))
        try:
            value = float(row.get(value_key, 0) or 0)
        except Exception:
            value = 0.0
        temp.append({"label": label, "value": value})

    max_value = max([r["value"] for r in temp], default=1) or 1
    out = []
    for r in temp:
        out.append(
            {
                "label": r["label"],
                "value": r["value"],
                "value_display": f"{r['value']:.1f}" if abs(r["value"]) < 1000 else f"{int(round(r['value'])):,}",
                "width_pct": round((r["value"] / max_value) * 100, 1) if max_value else 0,
            }
        )
    return out


def _segment_comp_rows(seg_df: pd.DataFrame) -> list[dict]:
    rows = _pick_top_rows(seg_df, ["인원"], limit=8, ascending=False)
    if not rows:
        return []

    total = sum(_safe_int(r.get("인원", 0)) for r in rows) or 1
    out = []
    for row in rows:
        people = _safe_int(row.get("인원", 0))
        out.append(
            {
                "label": str(row.get("세그먼트", "-")),
                "value": people,
                "value_display": f"{people:,}명 · {people / total * 100:.1f}%",
                "width_pct": round(people / total * 100, 1),
            }
        )
    return out


def _ml_grade_label(grade: Any) -> str:
    return {
        "Critical": "즉시 관리",
        "High": "관리 필요",
        "Medium": "관심 필요",
        "Low": "안정",
    }.get(str(grade), str(grade) if grade is not None else "-")


def _num_series(df: pd.DataFrame, col: str, default: float = 0.0) -> pd.Series:
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce").fillna(default)
    return pd.Series(default, index=df.index, dtype=float)


def _prepare_ml_pdf_view(ml_df: pd.DataFrame) -> pd.DataFrame:
    if ml_df is None or not isinstance(ml_df, pd.DataFrame) or ml_df.empty:
        return pd.DataFrame()

    df = ml_df.copy()

    df["churn_prob"] = _num_series(df, "churn_prob", 0.0).clip(lower=0, upper=1)
    df["recency_days"] = _num_series(df, "recency_days", 0.0)
    df["lifetime_sales"] = _num_series(df, "lifetime_sales", 0.0).clip(lower=0)
    df["sales_sum_30d"] = _num_series(df, "sales_sum_30d", 0.0).clip(lower=0)
    df["sales_sum_90d"] = _num_series(df, "sales_sum_90d", 0.0).clip(lower=0)
    df["sales_sum_180d"] = _num_series(df, "sales_sum_180d", 0.0).clip(lower=0)

    recent_30_actual = df["sales_sum_30d"].round(0)
    recent_90_monthly = (df["sales_sum_90d"] / 3.0).round(0)
    recent_180_monthly = (df["sales_sum_180d"] / 6.0).round(0)

    blended_base = recent_30_actual * 0.70 + recent_90_monthly * 0.20 + recent_180_monthly * 0.10
    fallback_base = recent_90_monthly.where(recent_90_monthly > 0, recent_180_monthly).where(lambda s: s > 0, 0)

    if "recent_30d_actual_sales" not in df.columns:
        df["recent_30d_actual_sales"] = recent_30_actual
    if "protection_value_base" not in df.columns:
        df["protection_value_base"] = blended_base.where(recent_30_actual > 0, fallback_base).fillna(0).round(0)

    if "protection_value" not in df.columns:
        df["protection_value"] = (df["churn_prob"] * df["protection_value_base"]).round(0)
    if "expected_loss_30d" not in df.columns:
        df["expected_loss_30d"] = df["protection_value"]
    else:
        df["expected_loss_30d"] = pd.to_numeric(df["expected_loss_30d"], errors="coerce").fillna(df["protection_value"])

    if "risk_grade" not in df.columns:
        # score_customers()를 거친 데이터는 이미 risk_grade가 채워져 있어 이 블록 자체가 스킵됨.
        # 여기서는 옛 캐시/CSV처럼 risk_grade 없이 들어오는 경우를 위한 폴백으로만 동작.
        df["risk_grade"] = compute_risk_grade(df)

    if "recommended_action" not in df.columns:
        recency = df["recency_days"]
        df["recommended_action"] = df["risk_grade"].map(
            {
                "Critical": "쿠폰 발송 + 재구매 알림",
                "High": "재구매 알림 발송",
                "Medium": "관심상품 재노출",
                "Low": "일반 CRM 유지",
            }
        )
        df.loc[(df["risk_grade"] == "Low") & (recency >= 90), "recommended_action"] = "휴면 복귀 메시지 발송"

    if "고객ID" not in df.columns:
        for cand in ["customer_id", "CustomerID", "user_id", "id"]:
            if cand in df.columns:
                df["고객ID"] = df[cand]
                break
    if "last_order_date" in df.columns:
        try:
            df["last_order_date"] = pd.to_datetime(df["last_order_date"], errors="coerce").dt.strftime("%Y-%m-%d")
        except Exception:
            pass

    return df


def _build_ml_risk_bar_rows(ml_view: pd.DataFrame) -> list[dict]:
    if ml_view.empty or "risk_grade" not in ml_view.columns:
        return []
    order = ["Critical", "High", "Medium", "Low"]
    temp = (
        ml_view["risk_grade"]
        .astype(str)
        .value_counts()
        .reindex(order, fill_value=0)
        .reset_index()
    )
    temp.columns = ["risk_grade", "고객수"]
    temp["위험상태"] = temp["risk_grade"].map(_ml_grade_label)
    rows = _make_bar_rows(temp.to_dict(orient="records"), "위험상태", "고객수", max_items=4)
    total = sum(r["value"] for r in rows) or 1
    for row in rows:
        row["value_display"] = f"{int(round(row['value'])):,}명"
        row["share_pct"] = round(row["value"] / total * 100, 1)
    return rows


def _build_ml_recency_bar_rows(ml_view: pd.DataFrame) -> list[dict]:
    if ml_view.empty:
        return []
    recency = _num_series(ml_view, "recency_days", 0)
    bins = [-1, 30, 60, 90, 180, 10**9]
    labels = ["0-30일", "31-60일", "61-90일", "91-180일", "181일+"]
    bucket = pd.cut(recency, bins=bins, labels=labels)
    temp = bucket.value_counts().reindex(labels, fill_value=0).reset_index()
    temp.columns = ["휴면구간", "고객수"]
    rows = _make_bar_rows(temp.to_dict(orient="records"), "휴면구간", "고객수", max_items=5)
    for row in rows:
        row["value_display"] = f"{int(round(row['value'])):,}명"
    return rows


def _build_ml_action_rows(ml_view: pd.DataFrame) -> list[dict]:
    if ml_view.empty or "recommended_action" not in ml_view.columns:
        return []
    temp = (
        ml_view["recommended_action"]
        .fillna("추천 액션 없음")
        .astype(str)
        .value_counts()
        .reset_index()
    )
    temp.columns = ["추천액션", "고객수"]
    rows = _make_bar_rows(temp.to_dict(orient="records"), "추천액션", "고객수", max_items=4)
    for row in rows:
        row["value_display"] = f"{int(round(row['value'])):,}명"
    return rows


def _build_ml_insight_rows(ml_view: pd.DataFrame) -> list[dict]:
    if ml_view.empty:
        return []

    insights: list[dict] = []

    recency_rows = _build_ml_recency_bar_rows(ml_view)
    if recency_rows:
        top_bucket = max(recency_rows, key=lambda r: r.get("value", 0))
        insights.append({"항목": "가장 많은 경과일 구간", "내용": f"{top_bucket['label']} · {int(round(top_bucket['value'])):,}명"})

    critical_value = 0
    if "risk_grade" in ml_view.columns and "expected_loss_30d" in ml_view.columns:
        critical_value = _safe_int(ml_view.loc[ml_view["risk_grade"] == "Critical", "expected_loss_30d"].fillna(0).sum(), 0)
    insights.append({"항목": "즉시 관리 고객의 방어 가치", "내용": f"30일 기준 {_fmt_currency(critical_value)}"})

    action_rows = _build_ml_action_rows(ml_view)
    if action_rows:
        top_action = action_rows[0]
        insights.append({"항목": "가장 많은 추천 액션", "내용": f"{top_action['label']} · {int(round(top_action['value'])):,}명"})

    return insights[:4]


def _prepare_ml_priority_table(ml_view: pd.DataFrame, limit: int = 18) -> list[dict]:
    if ml_view.empty:
        return []

    df = ml_view.copy()
    if "risk_grade" in df.columns:
        df = df[df["risk_grade"].isin(["Critical", "High"])]
    if "expected_loss_30d" in df.columns:
        df = df.sort_values("expected_loss_30d", ascending=False, na_position="last")
    elif "churn_prob" in df.columns:
        df = df.sort_values("churn_prob", ascending=False, na_position="last")

    out = pd.DataFrame()
    out["고객ID"] = df.get("고객ID", pd.Series(["-"] * len(df), index=df.index))
    out["위험상태"] = df.get("risk_grade", pd.Series(["-"] * len(df), index=df.index)).map(_ml_grade_label)
    out["최근 구매일"] = df.get("last_order_date", pd.Series(["-"] * len(df), index=df.index)).fillna("-")
    out["휴면일수"] = _num_series(df, "recency_days", 0).round(0).astype(int)
    out["누적매출"] = _num_series(df, "lifetime_sales", 0).round(0).apply(_fmt_currency)
    out["예상방어가치"] = _num_series(df, "expected_loss_30d", 0).round(0).apply(_fmt_currency)
    out["추천액션"] = df.get("recommended_action", pd.Series(["-"] * len(df), index=df.index)).fillna("-")
    out["이탈확률"] = _num_series(df, "churn_prob", 0).mul(100).round(1).astype(str) + "%"

    return _df_records(out, limit=limit)


def _build_context(
    title: str,
    user_name: str,
    run_name: str,
    kpi: dict,
    category_df: pd.DataFrame,
    segment_df: pd.DataFrame,
    customer_df: pd.DataFrame,
    ml_df: pd.DataFrame,
    refund_df: pd.DataFrame,
    inventory_df: pd.DataFrame,
    forecast: dict | None,
    selected_sections: dict,
    refund_rate: float | None = None,
    negative_sales_mode: str | None = None,
) -> dict:
    sections = _normalize_sections(selected_sections)

    category_rows = _pick_top_rows(category_df, ["위험", "평균위험", "risk_score", "총매출"], limit=8, ascending=False)
    segment_rows = _pick_top_rows(segment_df, ["인원", "평균위험"], limit=8, ascending=False)

    top_seg = str(segment_rows[0].get("세그먼트", "-")) if segment_rows else "-"
    top_cat = str(category_rows[0].get("카테고리", "-")) if category_rows else "-"

    refund_rate = _safe_float(refund_rate) if refund_rate is not None else 0.0

    ml_view = _prepare_ml_pdf_view(ml_df)

    critical_count = int(ml_view["risk_grade"].eq("Critical").sum()) if not ml_view.empty and "risk_grade" in ml_view.columns else 0
    high_risk_count = int(ml_view["risk_grade"].isin(["Critical", "High"]).sum()) if not ml_view.empty and "risk_grade" in ml_view.columns else 0
    high_manage_count = int(ml_view["risk_grade"].eq("High").sum()) if not ml_view.empty and "risk_grade" in ml_view.columns else 0
    medium_count = int(ml_view["risk_grade"].eq("Medium").sum()) if not ml_view.empty and "risk_grade" in ml_view.columns else 0

    protection_value_total = _safe_int(ml_view.get("expected_loss_30d", pd.Series(dtype=float)).fillna(0).sum(), 0) if not ml_view.empty else 0

    action_rows = _build_ml_action_rows(ml_view)
    at_risk_view = ml_view[ml_view["risk_grade"].isin(["Critical", "High"])] if not ml_view.empty and "risk_grade" in ml_view.columns else ml_view
    at_risk_actions = _build_ml_action_rows(at_risk_view)
    top_action_label = at_risk_actions[0]["label"] if at_risk_actions else "-"

    summary_lines = _summary_lines_from_kpi(
        kpi,
        top_seg,
        top_cat,
        refund_rate,
        protection_value=protection_value_total,
        critical_count=critical_count,
        high_risk_count=high_risk_count,
        top_action=top_action_label,
    )

    ml_risk_rows = _build_ml_risk_bar_rows(ml_view)
    ml_recency_rows = _build_ml_recency_bar_rows(ml_view)
    ml_action_rows = action_rows
    ml_insight_rows = _build_ml_insight_rows(ml_view)
    ml_priority_rows = _prepare_ml_priority_table(ml_view, limit=18)

    refund_pdf_df = _select_existing_columns(
        refund_df,
        ["카테고리", "주문수", "환불수", "환불금액", "환불률"],
        limit=10,
    )
    if not refund_pdf_df.empty and "환불률" in refund_pdf_df.columns:
        try:
            rr = pd.to_numeric(refund_pdf_df["환불률"], errors="coerce")
            refund_pdf_df["환불률"] = rr.mul(100).round(1).astype(str) + "%"
        except Exception:
            pass
    if not refund_pdf_df.empty and "환불금액" in refund_pdf_df.columns:
        refund_pdf_df["환불금액"] = refund_pdf_df["환불금액"].apply(_fmt_currency)
    refund_rows = _df_records(refund_pdf_df, limit=10)

    inventory_pdf_df = _select_existing_columns(
        inventory_df,
        ["펫카테고리", "카테고리", "예상판매량", "안전재고량", "권장보유일수", "우선순위"],
        limit=8,
    )
    if not inventory_pdf_df.empty:
        if "안전재고량" in inventory_pdf_df.columns:
            inventory_pdf_df["안전재고량"] = inventory_pdf_df["안전재고량"].apply(
                lambda x: f"약 {_safe_int(x):,}개" if str(x).strip() != "" else ""
            )
        if "예상판매량" in inventory_pdf_df.columns:
            try:
                inventory_pdf_df["예상판매량"] = pd.to_numeric(inventory_pdf_df["예상판매량"], errors="coerce").round(1)
            except Exception:
                pass
    inventory_rows = _df_records(inventory_pdf_df, limit=8)

    forecast = forecast if isinstance(forecast, dict) else {}
    forecast_label = str(forecast.get("label") or "다음 달 예상 매출").replace("다음달", "다음 달")
    forecast_value = _safe_int(forecast.get("value", kpi.get("expected_loss", 0)))
    negative_sales_mode = negative_sales_mode or forecast.get("negative_sales_mode") or "refund"

    overview_bar_rows = _make_bar_rows(category_rows, "카테고리", "위험", max_items=7) if category_rows else []
    segment_comp = _segment_comp_rows(segment_df)
    segment_risk_bars = _make_bar_rows(segment_rows, "세그먼트", "평균위험", max_items=8)

    category_bar_rows = []
    if category_rows:
        if "위험" in category_rows[0]:
            category_bar_rows = _make_bar_rows(category_rows, "카테고리", "위험", max_items=8)
        elif "평균위험" in category_rows[0]:
            category_bar_rows = _make_bar_rows(category_rows, "카테고리", "평균위험", max_items=8)
        elif "총매출" in category_rows[0]:
            category_bar_rows = _make_bar_rows(category_rows, "카테고리", "총매출", max_items=8)

    category_insights = []
    if category_rows:
        cat_label_key = "카테고리"
        risk_key = next((k for k in ["위험", "평균위험"] if k in category_rows[0]), None)
        if risk_key:
            vals = [(_safe_float(r.get(risk_key)), str(r.get(cat_label_key, "-")), r) for r in category_rows]
            vals.sort(key=lambda x: x[0], reverse=True)
            top_v, top_name, _ = vals[0]
            low_v, low_name, _ = vals[-1]
            category_insights.append(f"{top_name}의 평균 위험 점수가 {top_v:.0f}점으로 가장 높습니다.")
            category_insights.append(f"가장 낮은 {low_name}({low_v:.0f}점)과의 차이는 {top_v - low_v:.0f}점입니다.")
        cnt_key = next((k for k in ["고객수", "인원"] if k in category_rows[0]), None)
        if cnt_key:
            big = max(category_rows, key=lambda r: _safe_float(r.get(cnt_key)))
            category_insights.append(f"고객이 가장 많은 카테고리는 {big.get(cat_label_key, '-')}({_safe_int(big.get(cnt_key)):,}명)입니다.")
        category_insights.append("위험 점수가 높고 고객이 많은 카테고리부터 재구매 알림과 상품 구성을 점검하세요.")

    seg_top = segment_comp[0]["label"] if segment_comp else "-"
    if top_seg == "-" and seg_top != "-":
        top_seg = seg_top
    action_plan = [
        {"title": "반복 소비 카테고리 재구매 방어", "body": "사료·패드·모래 등은 재구매 주기 3~7일 전에 리마인드와 정기배송을 제안합니다."},
        {"title": f"즉시 관리 고객 {critical_count:,}명 우선 접촉", "body": "위험도 상위 10% 고객에게 쿠폰과 재구매 알림을 먼저 보냅니다."},
        {"title": f"{top_cat if top_cat != '-' else '위험 카테고리'} 집중 점검", "body": "위험 점수가 가장 높은 카테고리의 가격·배송·상품 구성을 점검합니다."},
    ]

    return {
        "generated_at": datetime.now().strftime("%Y.%m.%d"),
        "font_url": (STATIC_DIR / "fonts" / "PretendardVariable.woff2").resolve().as_uri(),
        "action_plan": action_plan,
        "category_insights": category_insights[:4],
        "title": title,
        "user_name": user_name,
        "run_name": run_name,
        "sections": sections,
        "negative_sales_mode_label": _negative_sales_mode_label(negative_sales_mode),
        "negative_sales_mode_desc": _negative_sales_mode_desc(negative_sales_mode),
        "summary": {
            "total_customers": _fmt_int(kpi.get("total_customers", len(ml_view) if not ml_view.empty else 0)),
            "high_ratio": f"{_safe_float(kpi.get('high_ratio', 0)):.1f}%",
            "avg_risk": f"{_safe_float(kpi.get('avg_risk', 0)):.0f}점",
            "expected_loss": _fmt_currency(kpi.get("expected_loss", 0)),
            "protection_value": _fmt_currency(protection_value_total),
            "protection_value_short": _fmt_krw_short(protection_value_total),
            "expected_loss_short": _fmt_krw_short(kpi.get("expected_loss", 0)),
            "forecast_value_short": _fmt_krw_short(forecast_value),
            "critical_count": _fmt_int(critical_count),
            "high_risk_count": _fmt_int(high_risk_count),
            "high_manage_count": _fmt_int(high_manage_count),
            "medium_count": _fmt_int(medium_count),
            "refund_rate": f"{refund_rate * 100:.1f}%",
            "forecast_label": forecast_label,
            "forecast_value": _fmt_currency(forecast_value),
            "top_action_label": top_action_label,
        },
        "summary_lines": summary_lines,
        "overview_bar_rows": overview_bar_rows,
        "segment_comp_rows": segment_comp,
        "segment_risk_rows": segment_risk_bars,
        "segment_rows": segment_rows,
        "category_rows": category_rows,
        "category_bar_rows": category_bar_rows,
        "ml_rows": ml_priority_rows,
        "ml_risk_rows": ml_risk_rows,
        "ml_recency_rows": ml_recency_rows,
        "ml_action_rows": ml_action_rows,
        "ml_insight_rows": ml_insight_rows,
        "refund_rows": refund_rows,
        "inventory_rows": inventory_rows,
    }


def build_report_pdf(
    title: str,
    user_name: str,
    run_name: str,
    kpi: dict,
    category_df: pd.DataFrame,
    segment_df: pd.DataFrame,
    customer_df: pd.DataFrame,
    ml_df: pd.DataFrame,
    refund_df: pd.DataFrame,
    inventory_df: pd.DataFrame,
    forecast: dict | None = None,
    selected_sections: dict | None = None,
    refund_rate: float | None = None,
    negative_sales_mode: str | None = None,
) -> bytes:
    env = _env()
    template = env.get_template("report_base.html")

    category_df = category_df if isinstance(category_df, pd.DataFrame) else pd.DataFrame()
    segment_df = segment_df if isinstance(segment_df, pd.DataFrame) else pd.DataFrame()
    customer_df = customer_df if isinstance(customer_df, pd.DataFrame) else pd.DataFrame()
    ml_df = ml_df if isinstance(ml_df, pd.DataFrame) else pd.DataFrame()
    refund_df = refund_df if isinstance(refund_df, pd.DataFrame) else pd.DataFrame()
    inventory_df = inventory_df if isinstance(inventory_df, pd.DataFrame) else pd.DataFrame()

    context = _build_context(
        title=title,
        user_name=user_name,
        run_name=run_name,
        kpi=kpi or {},
        category_df=category_df,
        segment_df=segment_df,
        customer_df=customer_df,
        ml_df=ml_df,
        refund_df=refund_df,
        inventory_df=inventory_df,
        forecast=forecast,
        selected_sections=selected_sections or {},
        refund_rate=refund_rate,
        negative_sales_mode=negative_sales_mode,
    )

    temp_dir = Path(tempfile.mkdtemp(prefix="pet_pdf_"))
    html_path = temp_dir / "report.html"
    pdf_path = temp_dir / "report.pdf"
    payload_path = temp_dir / "payload.json"

    html = template.render(**context)
    html_path.write_text(html, encoding="utf-8")

    payload = {
        "html_path": str(html_path),
        "pdf_path": str(pdf_path),
        "css_path": str((STATIC_DIR / "pdf_report.css").resolve()),
    }
    payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    worker_path = Path(__file__).resolve().parent / "pdf_render_worker.py"
    completed = subprocess.run(
        [sys.executable, str(worker_path), str(payload_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    if completed.returncode != 0:
        raise RuntimeError(
            "PDF 렌더링 실패\n"
            f"STDOUT:\n{completed.stdout}\n\n"
            f"STDERR:\n{completed.stderr}"
        )

    return pdf_path.read_bytes()
