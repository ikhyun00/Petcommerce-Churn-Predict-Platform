import pandas as pd
import plotly.express as px
import streamlit as st

from .analytics import compute_rfm_and_risk
from .report_component import section_header, metric_card, chart_card, insight_box, action_card, table_block


def _fmt_currency(x) -> str:
    try:
        return f"₩{int(round(float(x))):,}"
    except Exception:
        return "-"


def _fmt_int(x) -> str:
    try:
        return f"{int(x):,}"
    except Exception:
        return "-"


def _fmt_percent(x) -> str:
    try:
        return f"{float(x):.1f}%"
    except Exception:
        return "-"


def free_report_step(df_std: pd.DataFrame):
    result = compute_rfm_and_risk(df_std)
    kpi = result["kpi"]
    seg = result["segment_summary"]
    cat = result["category_risk"]
    cust = result["customer_list"]
    refund = result.get("refund", {}) or {}

    st.markdown(
        """
        <div class="page-head">
          <div class="crumb">리포트 · <b>무료 플랜</b></div>
          <div class="page-title">간단 이탈 리포트</div>
          <div class="page-subtitle">핵심 지표와 우선 대응 고객만 빠르게 확인하는 요약 리포트입니다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        metric_card("전체 고객 수", f"{_fmt_int(kpi.get('total_customers', 0))}명", "업로드 데이터 기준")
    with c2:
        metric_card("고위험 고객 비율", _fmt_percent(kpi.get('high_ratio', 0)), "위험 점수 70점 이상")
    with c3:
        metric_card("예상 이탈 매출", _fmt_currency(kpi.get('expected_loss', 0)), "고위험 고객 기준 추정 손실")
    with c4:
        metric_card("환불률", _fmt_percent(float(refund.get('refund_rate', 0) or 0) * 100), "상품·배송 이슈 참고")

    bullets = [
        f"현재 고위험 고객 비율은 {_fmt_percent(kpi.get('high_ratio', 0))} 수준입니다.",
        f"고위험 고객 기준 추정 이탈 매출은 {_fmt_currency(kpi.get('expected_loss', 0))}입니다.",
        "무료 플랜은 규칙 기반 위험 점수로 계산합니다. ML 이탈예측은 Pro에서 볼 수 있어요.",
    ]
    insight_box("핵심 요약", bullets, tone="info")

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        if isinstance(seg, pd.DataFrame) and not seg.empty and {"세그먼트", "인원"}.issubset(seg.columns):
            fig = px.pie(seg, names="세그먼트", values="인원", hole=0.55)
            fig.update_traces(textposition="inside", textinfo="percent+label")
            chart_card("고객 세그먼트 구성", fig, "고객군별 인원 비중입니다.")
        else:
            st.info("세그먼트 데이터가 없습니다.")

    with col2:
        if isinstance(cat, pd.DataFrame) and not cat.empty and {"카테고리", "위험"}.issubset(cat.columns):
            cat_plot = cat.sort_values("위험", ascending=True).copy()
            fig = px.bar(cat_plot, x="위험", y="카테고리", orientation="h", text="위험", color_discrete_sequence=["#4F46E5"])
            fig.update_layout(xaxis_title="평균 위험 점수", yaxis_title="")
            fig.update_traces(textposition="outside")
            chart_card("카테고리별 위험 점수", fig, "점수가 높은 카테고리부터 관리가 필요합니다.")
        else:
            st.info("카테고리 데이터가 없습니다.")

    section_header("우선 대응 고객", "위험 점수가 높은 고객 10명입니다.")
    if isinstance(cust, pd.DataFrame) and not cust.empty:
        show = cust.copy().head(10)
        if "주문금액" in show.columns:
            show["주문금액"] = show["주문금액"].apply(_fmt_currency)
        table_block(show, height=340)
    else:
        st.info("고객 리스트가 없습니다.")

    section_header("바로 실행할 액션", "지금 바로 할 수 있는 운영 액션입니다.")
    action_card("고위험 고객 재구매 유도", "최근 구매가 끊긴 고객에게 리마인드 메시지와 재구매 쿠폰을 우선 발송하세요.", "우선순위 1")
    action_card("위험 카테고리 집중 관리", "위험도가 높은 카테고리의 상품 설명, 배송, 가격 조건을 우선 점검하세요.", "우선순위 2")
    action_card("VIP 고객 이탈 방지", "구매 금액이 큰 고객은 별도 혜택과 개인화 추천으로 선제 케어하는 것이 좋습니다.", "우선순위 3")

    st.info("Pro에서는 ML 이탈예측, 카테고리 재구매 주기, 환불·재고 전략, PDF 리포트까지 볼 수 있습니다. 왼쪽 분석 모드에서 Pro를 선택하세요.")