import html

import pandas as pd
import streamlit as st

from src.auth import login_gate, logout_user, restore_auth_from_session, signup_form
from src.data_io import load_csv_or_sample_sidebar
from src.free_ui import free_report_step
from src.mapping_ui import mapping_step
from src.report_ui import report_step
from src.storage import init_db, list_runs, activate_pro_membership, get_user_membership_status
from src.style import apply_style, render_top_hero
from src.style_token import apply_design_tokens


st.set_page_config(
    page_title="Pet Commerce Analytics",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
restore_auth_from_session()

DIALOG = getattr(st, "dialog", None) or getattr(st, "experimental_dialog", None)

for key, value in {
    "user_key": "guest",
    "auth_token": None,
    "service_mode": "free",
    "pro_paid": False,
    "pro_expires_at": None,
    "pro_days_left": 0,
    "modal": None,
    "step": 0,
    "view_run_id": None,
    "sidebar_run_pick": "현재 분석",
    "df_raw": None,
    "df_std": None,
    "upload_period_days": None,
    "upload_short_period_warning": False,
    "upload_short_period_message": "",
    "analysis_ready": False,
    "prev_step": 0,
    "show_report_loading_overlay": False,
}.items():
    st.session_state.setdefault(key, value)


apply_style()
apply_design_tokens()

_is_logged_in = st.session_state.get("user_key", "guest") != "guest"
_is_pro_mode = st.session_state.get("service_mode") == "pro" and st.session_state.get("pro_paid", False)
render_top_hero(
    "Pro" if _is_pro_mode else "무료 플랜",
    st.session_state["user_key"] if _is_logged_in else None,
    is_pro=_is_pro_mode,
)


def _fmt_saved_at(x) -> str:
    try:
        if x is None or str(x).strip() == "":
            return ""
        return pd.to_datetime(x).strftime("%m.%d %H:%M")
    except Exception:
        return str(x) if x is not None else ""


def _make_run_label(run: dict) -> str:
    title = str((run.get("run_name") or "")).strip() or "저장한 분석"
    saved_at = _fmt_saved_at(run.get("created_at", ""))
    return f"{title}  ·  {saved_at}" if saved_at else title


def _clear_saved_run_view():
    st.session_state["view_run_id"] = None
    st.session_state["sidebar_run_pick"] = "현재 분석"


def _go_home():
    st.session_state["step"] = 0
    st.session_state["view_run_id"] = None
    st.session_state["sidebar_run_pick"] = "현재 분석"
    st.session_state["df_raw"] = None
    st.session_state["df_std"] = None
    st.session_state["analysis_ready"] = False
    st.session_state["prev_step"] = 0
    st.session_state["show_report_loading_overlay"] = False
    st.session_state.pop("analysis_saved", None)
    st.rerun()


def _start_new_analysis(df: pd.DataFrame):
    st.session_state["df_raw"] = df
    st.session_state["df_std"] = None
    st.session_state["mapping_confirmed"] = False
    st.session_state["quality_result"] = None
    st.session_state["analysis_ready"] = False
    st.session_state.pop("analysis_saved", None)
    _clear_saved_run_view()
    st.session_state["step"] = 1


def _render_sidebar_account():
    with st.sidebar:
        st.markdown('<div class="side-section-title">계정</div>', unsafe_allow_html=True)
        if _is_logged_in:
            user = st.session_state["user_key"]
            if st.session_state.get("pro_paid", False):
                meta = f"Pro 이용 중 · {st.session_state.get('pro_days_left', 0)}일 남음"
            else:
                meta = "무료 플랜"
            st.markdown(
                f"""
                <div class="side-user">
                  <div class="avatar">{html.escape(user[:1].upper())}</div>
                  <div><div class="name">{html.escape(user)}</div><div class="meta">{meta}</div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("로그아웃", key="side_logout", use_container_width=True):
                st.session_state["modal"] = "logout"
        else:
            st.markdown('<div class="sidebar-note">로그인하면 분석을 저장하고 다시 불러올 수 있어요.</div>', unsafe_allow_html=True)
            a, b = st.columns(2)
            if a.button("로그인", key="side_login", type="primary", use_container_width=True):
                st.session_state["modal"] = "login"
            if b.button("회원가입", key="side_signup", use_container_width=True):
                st.session_state["modal"] = "signup"


def _render_sidebar_mode():
    with st.sidebar:
        st.markdown('<div class="side-section-title">분석 모드</div>', unsafe_allow_html=True)
        is_pro_mode = st.session_state.get("service_mode") == "pro"
        c1, c2 = st.columns(2)
        if c1.button("무료", key="mode_free", type="secondary" if is_pro_mode else "primary", use_container_width=True):
            st.session_state["service_mode"] = "free"
            st.session_state["mode_chosen"] = True
            st.rerun()
        if c2.button("Pro", key="mode_pro", type="primary" if is_pro_mode else "secondary", use_container_width=True):
            if st.session_state.get("pro_paid", False):
                st.session_state["service_mode"] = "pro"
                st.session_state["mode_chosen"] = True
                st.rerun()
            else:
                st.session_state["modal"] = "payment"
        if not is_pro_mode:
            st.markdown('<div class="sidebar-note">Pro에서는 ML 이탈예측, 카테고리·재고 분석, PDF 리포트를 볼 수 있어요.</div>', unsafe_allow_html=True)


def _render_sidebar_navigation():
    with st.sidebar:
        if st.session_state.get("step", 0) >= 1:
            st.markdown('<div class="side-section-title">분석</div>', unsafe_allow_html=True)
            if st.button("＋  새 분석 시작", key="nav_home", use_container_width=True):
                _go_home()

        st.markdown('<div class="side-section-title">최근 저장한 분석</div>', unsafe_allow_html=True)
        if not _is_logged_in:
            st.markdown('<div class="sidebar-note">로그인 후 저장한 분석이 여기에 표시됩니다.</div>', unsafe_allow_html=True)
            return

        try:
            runs = list_runs(st.session_state["user_key"])
        except Exception as e:
            st.caption("저장 기록을 불러오지 못했습니다.")
            st.exception(e)
            return

        if not runs:
            st.markdown('<div class="sidebar-note">아직 저장한 분석이 없어요.</div>', unsafe_allow_html=True)
            return

        current = st.session_state.get("view_run_id")
        for r in runs[:6]:
            rid = r.get("run_id")
            if rid is None:
                continue
            key = f"recent_run_on_{rid}" if current == rid else f"recent_run_{rid}"
            if st.button(_make_run_label(r), key=key, use_container_width=True):
                st.session_state["view_run_id"] = rid
                st.session_state["sidebar_run_pick"] = rid
                st.session_state["step"] = 2
                st.rerun()


_render_sidebar_account()
_render_sidebar_mode()
_render_sidebar_navigation()


def _render_login_ui():
    authed, _, username = login_gate()
    if authed and username:
        st.session_state["user_key"] = username
        st.session_state["modal"] = None
        st.success("로그인했습니다.")
        st.rerun()
    if st.button("계정이 없나요? 회원가입", key="dlg_to_signup", use_container_width=True):
        st.session_state["modal"] = "signup"
        st.rerun()


def _render_signup_ui():
    signup_form()
    if st.button("이미 계정이 있나요? 로그인", key="dlg_to_login", use_container_width=True):
        st.session_state["modal"] = "login"
        st.rerun()


def _render_logout_ui():
    st.write("로그아웃하면 저장하지 않은 현재 분석은 사라집니다.")
    c1, c2 = st.columns(2)
    if c1.button("취소", use_container_width=True):
        st.session_state["modal"] = None
        st.rerun()
    if c2.button("로그아웃", type="primary", use_container_width=True):
        logout_user()
        st.session_state["modal"] = None
        st.session_state["service_mode"] = "free"
        st.session_state["mode_chosen"] = False
        st.session_state["pro_paid"] = False
        st.session_state["view_run_id"] = None
        st.session_state["sidebar_run_pick"] = "현재 분석"
        st.session_state["df_raw"] = None
        st.session_state["df_std"] = None
        st.session_state["analysis_ready"] = False
        st.session_state["show_report_loading_overlay"] = False
        st.session_state.pop("analysis_saved", None)
        st.rerun()


def _render_payment_ui():
    st.caption("데모 결제입니다. 실제 결제는 이뤄지지 않고, 결제 기록만 저장되어 Pro 권한이 30일간 유지됩니다.")

    current_user = st.session_state.get("user_key", "guest")
    if current_user == "guest":
        st.info("Pro 권한을 계정에 연결하려면 먼저 로그인해주세요.")
        c1, c2 = st.columns(2)
        if c1.button("닫기", use_container_width=True):
            st.session_state["modal"] = None
            st.rerun()
        if c2.button("로그인", type="primary", use_container_width=True):
            st.session_state["modal"] = "login"
            st.rerun()
        return

    status = get_user_membership_status(current_user)
    if status.get("is_pro"):
        st.success(
            f"Pro 이용 중입니다. 만료일 {status.get('pro_expires_at')} (약 {status.get('days_left', 0)}일 남음)"
        )

    with st.form("payment_form", border=False):
        st.markdown("**Pro 월간 · ₩4,900**")
        name = st.text_input("이름", value=current_user)
        email = st.text_input("이메일")
        card_number = st.text_input("카드번호", placeholder="1234-5678-9012-3456")
        c1, c2 = st.columns(2)
        expiry = c1.text_input("유효기간", placeholder="MM/YY")
        cvc = c2.text_input("CVC", placeholder="123")
        pay_ok = st.form_submit_button("결제하고 Pro 시작", type="primary", use_container_width=True)

    if pay_ok:
        if not (name and email and card_number and expiry and cvc):
            st.error("모든 항목을 입력해주세요.")
            return

        try:
            payment = activate_pro_membership(
                username=current_user,
                payer_name=name,
                email=email,
                plan="pro_monthly",
                amount=4900,
                duration_days=30,
            )
            st.session_state["pro_paid"] = True
            st.session_state["service_mode"] = "pro"
            st.session_state["pro_expires_at"] = payment.get("expires_at")
            refreshed = get_user_membership_status(current_user)
            st.session_state["pro_days_left"] = refreshed.get("days_left", 0)
            st.session_state["modal"] = None
            st.success(f"Pro가 시작되었습니다. {payment.get('expires_at')}까지 이용할 수 있습니다.")
            st.rerun()
        except Exception as e:
            st.error(f"결제 저장 중 오류가 발생했습니다: {e}")


if DIALOG is not None and st.session_state.get("modal") in {"login", "signup", "logout", "payment"}:
    modal = st.session_state.get("modal")
    if modal == "login":
        @DIALOG("로그인")
        def _login_dialog():
            _render_login_ui()
        _login_dialog()
    elif modal == "signup":
        @DIALOG("회원가입")
        def _signup_dialog():
            _render_signup_ui()
        _signup_dialog()
    elif modal == "logout":
        @DIALOG("로그아웃")
        def _logout_dialog():
            _render_logout_ui()
        _logout_dialog()
    elif modal == "payment":
        @DIALOG("Pro 업그레이드")
        def _payment_dialog():
            _render_payment_ui()
        _payment_dialog()


def _render_data_period_warning_banner():
    warning_on = st.session_state.get("upload_short_period_warning", False)
    message = st.session_state.get("upload_short_period_message", "")
    if warning_on and message:
        st.markdown(f'<div class="warn-banner">{message}</div>', unsafe_allow_html=True)


def _render_home_hero():
    st.markdown(
        """
        <div class="hero">
          <div class="hero-eyebrow">반려동물 커머스 CRM</div>
          <div class="hero-title">거래 데이터만 올리면<br><em>이탈 위험 고객</em>과 다음 액션까지</div>
          <div class="hero-sub">주문 내역을 업로드하면 고객별 이탈 위험을 예측하고, 누구를 먼저 챙겨야 하는지와 카테고리·환불·재고 포인트를 한 화면에 정리합니다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_stepper(active: int):
    steps = [
        ("데이터 업로드", "CSV · XLSX 또는 샘플 데이터"),
        ("컬럼 매핑", "표준 컬럼 연결과 품질 점검"),
        ("리포트", "이탈 예측과 실행 액션"),
    ]
    items = []
    for idx, (title, desc) in enumerate(steps):
        state = "on" if idx == active else ("done" if idx < active else "")
        num = "✓" if idx < active else str(idx + 1)
        items.append(
            f'<div class="step {state}"><div class="step-num">{num}</div>'
            f'<div><div class="step-title">{title}</div><div class="step-desc">{desc}</div></div></div>'
        )
    st.markdown(f'<div class="stepper">{"".join(items)}</div>', unsafe_allow_html=True)


def _render_home_features():
    icon_chart = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/></svg>'
    icon_users = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.8-3.5 3.4-5.5 6.5-5.5s5.7 2 6.5 5.5"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7"/><path d="M18 14.7c1.8.7 3 2.5 3.5 5.3"/></svg>'
    icon_doc = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/><path d="M9 13h6M9 17h4"/></svg>'
    st.markdown(
        f"""
        <div class="section-head"><div class="section-title">무엇을 볼 수 있나요</div></div>
        <div class="feature-grid">
          <div class="feature"><div class="feature-icon">{icon_chart}</div>
            <div class="feature-title">ML 이탈 예측</div>
            <div class="feature-desc">고객 이력 길이에 맞는 모델로 이탈 확률을 계산하고, 위험도 상위 30%를 즉시 관리·관리 필요 고객으로 나눕니다.</div></div>
          <div class="feature"><div class="feature-icon">{icon_users}</div>
            <div class="feature-title">세그먼트 · 카테고리 분석</div>
            <div class="feature-desc">RFM 세그먼트, 카테고리별 재구매 주기와 이탈 위험, 다반려 추정 고객을 운영 액션과 함께 보여줍니다.</div></div>
          <div class="feature"><div class="feature-icon">{icon_doc}</div>
            <div class="feature-title">저장 · 비교 · PDF</div>
            <div class="feature-desc">분석을 저장해 기간별로 비교하고, 필요한 탭만 골라 PDF 리포트로 내보낼 수 있습니다.</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


LOADING_HTML = """
<div class="loading-overlay">
  <div class="loading-modal">
    <div class="loading-title">리포트를 만드는 중입니다</div>
    <div class="loading-desc">이탈 예측과 세그먼트 분석을 계산하고 있어요. 잠시만 기다려주세요.</div>
    <div class="loading-dots"><span></span><span></span><span></span></div>
  </div>
</div>
"""


current_step = int(st.session_state.get("step", 0) or 0)
prev_step = int(st.session_state.get("prev_step", current_step) or current_step)

if current_step == 2 and prev_step == 1 and st.session_state.get("analysis_ready", False):
    st.session_state["show_report_loading_overlay"] = True

report_transition_loading = bool(st.session_state.get("show_report_loading_overlay", False))
st.session_state["prev_step"] = current_step


if st.session_state["step"] == 0:
    _render_home_hero()
    _render_stepper(0)
    _render_data_period_warning_banner()
    df = load_csv_or_sample_sidebar()
    if df is None:
        _render_home_features()
    else:
        _start_new_analysis(df)
        st.rerun()

elif st.session_state["step"] == 1:
    if st.session_state.get("df_raw") is None:
        st.warning("업로드된 데이터가 없습니다. 먼저 CSV 또는 XLSX 파일을 업로드해주세요.")
        st.session_state["step"] = 0
        st.session_state["analysis_ready"] = False
        st.session_state["prev_step"] = 0
        st.rerun()
    else:
        _render_stepper(1)
        df_std = mapping_step(st.session_state["df_raw"])
        if df_std is not None:
            st.session_state["df_std"] = df_std
            st.session_state["analysis_ready"] = True
            st.session_state.pop("analysis_saved", None)

else:
    selected_saved_run = st.session_state.get("view_run_id")

    if selected_saved_run is not None:
        overlay_placeholder = st.empty()

        if report_transition_loading:
            overlay_placeholder.markdown(LOADING_HTML, unsafe_allow_html=True)

        report_step(
            st.session_state.get("df_std", pd.DataFrame()),
            user_key=st.session_state.get("user_key", "guest"),
        )

        if report_transition_loading:
            overlay_placeholder.empty()
            st.session_state["show_report_loading_overlay"] = False
            st.rerun()

    else:
        if st.session_state.get("df_std") is None:
            st.warning("현재 분석할 데이터가 없습니다. 파일을 다시 업로드하거나 왼쪽에서 저장한 분석을 선택해주세요.")
            if st.button("업로드 화면으로", type="primary"):
                st.session_state["step"] = 0
                st.session_state["analysis_ready"] = False
                st.session_state["prev_step"] = 0
                st.session_state["show_report_loading_overlay"] = False
                st.rerun()
        else:
            overlay_placeholder = st.empty()

            if report_transition_loading:
                overlay_placeholder.markdown(LOADING_HTML, unsafe_allow_html=True)

            if st.session_state.get("service_mode") == "free":
                free_report_step(st.session_state["df_std"])
            else:
                if st.session_state.get("pro_paid", False):
                    report_step(
                        st.session_state["df_std"],
                        user_key=st.session_state["user_key"],
                    )
                else:
                    st.info("Pro 분석은 업그레이드 후 이용할 수 있습니다.")
                    if st.button("Pro 업그레이드", type="primary"):
                        st.session_state["modal"] = "payment"
                        st.rerun()

            if report_transition_loading:
                overlay_placeholder.empty()
                st.session_state["show_report_loading_overlay"] = False
