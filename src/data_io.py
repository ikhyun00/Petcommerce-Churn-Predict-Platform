import io
from io import BytesIO
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st


STD_REQUIRED = ["고객ID", "주문번호", "거래일시", "매출"]
STD_OPTIONAL = ["카테고리", "구매채널", "온라인채널", "결제수단", "시도"]


def make_sample_data(n_tx: int = 1500, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    customers = rng.integers(10000, 20000, size=300)
    cust_ids = rng.choice(customers, size=n_tx, replace=True)

    start = datetime(2024, 1, 1)
    end = datetime(2024, 6, 30)
    dates = pd.to_datetime(
        rng.integers(int(start.timestamp()), int(end.timestamp()), size=n_tx),
        unit="s",
    )

    date_str = np.where(
        rng.random(n_tx) < 0.5,
        dates.strftime("%Y/%m/%d %H:%M"),
        dates.strftime("%Y-%m-%d"),
    )

    order_ids = np.arange(1, n_tx + 1)
    categories = np.array(["사료", "간식", "장난감", "위생용품", "미용"])
    cat = rng.choice(categories, size=n_tx, p=[0.30, 0.30, 0.15, 0.15, 0.10])
    channel = rng.choice(["온라인", "오프라인"], size=n_tx, p=[0.78, 0.22])
    sido = rng.choice(
        ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "경기", "제주"],
        size=n_tx,
    )
    pay = rng.choice(
        ["카드", "현금", "계좌이체", "간편결제"],
        size=n_tx,
        p=[0.55, 0.15, 0.10, 0.20],
    )
    platform = rng.choice(
        ["스마트스토어", "쿠팡", "자사몰", "매장"],
        size=n_tx,
        p=[0.35, 0.35, 0.20, 0.10],
    )

    base = {
        "사료": 32000,
        "간식": 15000,
        "장난감": 22000,
        "위생용품": 18000,
        "미용": 26000,
    }
    amount = np.array([max(1000, int(rng.normal(base[c], base[c] * 0.45))) for c in cat])

    return pd.DataFrame(
        {
            "customer_no": cust_ids.astype(int),
            "order_id": order_ids.astype(int),
            "purchase_date": date_str,
            "total_price": [f"{x:,}" for x in amount],
            "product_group": cat,
            "sales_channel": channel,
            "platform_name": platform,
            "pay_type": pay,
            "region_name": sido,
            "상품명": rng.choice(["사료A", "간식B", "장난감C", "샴푸D", "패드E"], size=n_tx),
        }
    )


def get_sample_mapping_hint() -> dict:
    return {
        "고객ID": "customer_no",
        "주문번호": "order_id",
        "거래일시": "purchase_date",
        "매출": "total_price",
        "카테고리": "product_group",
        "구매채널": "sales_channel",
        "온라인채널": "platform_name",
        "결제수단": "pay_type",
        "시도": "region_name",
    }


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).strip() for c in df.columns]
    return df


def read_csv_safely(uploaded_file) -> pd.DataFrame:
    def _try_read(enc):
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding=enc, sep=None, engine="python")
        return _normalize_columns(df)

    for enc in ["utf-8", "cp949", None]:
        try:
            return _try_read(enc)
        except Exception:
            continue

    uploaded_file.seek(0)
    df = pd.read_csv(uploaded_file, encoding="cp949")
    return _normalize_columns(df)


def read_excel_safely(uploaded_file) -> pd.DataFrame:
    uploaded_file.seek(0)
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    return _normalize_columns(df)


def read_uploaded_table(uploaded_file) -> pd.DataFrame:
    file_name = (uploaded_file.name or "").lower()
    if file_name.endswith(".csv"):
        return read_csv_safely(uploaded_file)
    if file_name.endswith(".xlsx"):
        return read_excel_safely(uploaded_file)
    raise ValueError("CSV 또는 XLSX 파일만 업로드 가능합니다.")


def get_sample_csv_text(df: pd.DataFrame) -> str:
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


def get_sample_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    return buffer.getvalue()


def _render_page_css():
    st.markdown(
        """
<style>
div[data-testid="stFileUploader"] > label {
    display: none !important;
}

.st-key-upload_card, .st-key-sample_card {
    padding: 24px !important;
    height: 100%;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def _render_sidebar_compact_guide():
    with st.sidebar:
        st.markdown(
            """
<div class="side-section-title">업로드 기준</div>
<div class="side-guide">
  <b>CSV · XLSX 지원</b>
  고객ID · 주문번호 · 거래일시 · 매출 4개 컬럼만 있으면 시작할 수 있어요. 이탈 분석에는 3개월 이상 데이터를 권장합니다.
</div>
            """,
            unsafe_allow_html=True,
        )


def _set_short_period_state(span_days: int, message: str):
    st.session_state["upload_period_days"] = span_days
    st.session_state["upload_short_period_warning"] = True
    st.session_state["upload_short_period_message"] = message


def _clear_short_period_state():
    st.session_state["upload_period_days"] = None
    st.session_state["upload_short_period_warning"] = False
    st.session_state["upload_short_period_message"] = ""


def _check_short_period_warning(df: pd.DataFrame):
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        _clear_short_period_state()
        return

    date_candidates = [
        "거래일시", "purchase_date", "purchase_datetime", "order_date", "date",
        "주문일", "구매일", "거래일", "created_at", "timestamp",
    ]
    date_col = next((c for c in date_candidates if c in df.columns), None)
    if date_col is None:
        _clear_short_period_state()
        return

    dates = pd.to_datetime(df[date_col], errors="coerce", format="mixed").dropna()
    if dates.empty:
        _clear_short_period_state()
        return

    span_days = int((dates.max() - dates.min()).days)
    if span_days < 90:
        message = (
            f"업로드한 데이터 기간이 약 {span_days}일입니다. "
            "3개월 미만이면 재구매 주기와 이탈 분석 결과의 신뢰도가 낮아질 수 있어요."
        )
        _set_short_period_state(span_days, message)
    else:
        _clear_short_period_state()


def _render_upload_header():
    st.markdown(
        """
<div class="card-tag">시작하기</div>
<div class="card-title">거래 데이터 업로드</div>
<div class="card-desc">CSV 또는 XLSX 파일을 올리면 컬럼 매핑 → 품질 점검 → 리포트 순서로 진행됩니다.</div>
        """,
        unsafe_allow_html=True,
    )


def _render_sample_header():
    st.markdown(
        """
<div class="card-tag green">데이터가 없다면</div>
<div class="card-title">샘플 데이터로 체험하기</div>
<div class="card-desc">권장 양식의 샘플로 전체 흐름을 바로 확인할 수 있어요.</div>
        """,
        unsafe_allow_html=True,
    )


def load_csv_or_sample_sidebar() -> pd.DataFrame | None:
    _render_sidebar_compact_guide()
    _render_page_css()

    sample_df = make_sample_data()
    sample_csv = get_sample_csv_text(sample_df)
    sample_xlsx = get_sample_excel_bytes(sample_df)

    hero_col, sample_col = st.columns([1.6, 1.0], gap="medium")

    with hero_col:
        with st.container(border=True, key="upload_card"):
            _render_upload_header()

            up = st.file_uploader(
                "CSV 또는 XLSX 파일 선택",
                type=["csv", "xlsx"],
                help="업로드 후 다음 단계에서 컬럼을 매핑합니다.",
                label_visibility="collapsed",
            )
            st.markdown(
                '<div class="hint">재구매 주기와 이탈 분석을 위해 3개월 이상의 거래 데이터를 권장합니다.</div>',
                unsafe_allow_html=True,
            )

            if up is not None:
                try:
                    st.session_state.data_source = "upload"
                    df = read_uploaded_table(up)
                    _check_short_period_warning(df)

                    if st.session_state.get("upload_short_period_warning"):
                        st.warning(st.session_state.get("upload_short_period_message", ""))

                    st.success("업로드가 완료되었습니다. 다음 단계에서 컬럼을 매핑합니다.")
                    return df
                except Exception as e:
                    st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
                    return None

    with sample_col:
        with st.container(border=True, key="sample_card"):
            _render_sample_header()

            if st.button("샘플 데이터로 시작", type="primary", use_container_width=True):
                st.session_state.data_source = "sample"
                _check_short_period_warning(sample_df)
                st.success("샘플 데이터를 불러왔습니다. 다음 단계에서 컬럼을 매핑합니다.")
                return sample_df

            d1, d2 = st.columns(2)
            with d1:
                st.download_button(
                    "CSV 받기",
                    data=sample_csv,
                    file_name="sample_data.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with d2:
                st.download_button(
                    "XLSX 받기",
                    data=sample_xlsx,
                    file_name="sample_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

    return None
