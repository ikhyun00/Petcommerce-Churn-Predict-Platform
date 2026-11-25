import html

import streamlit as st


TOPBAR_H = 60


def apply_style():
    css = f"""
    <style>
    @import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css");

    :root {{
      --topbar-h: {TOPBAR_H}px;
    }}

    html {{
      scroll-behavior: smooth;
    }}

    header[data-testid="stHeader"] {{
      background: transparent !important;
      height: 0 !important;
    }}

    header[data-testid="stHeader"] [data-testid="stToolbar"],
    header[data-testid="stHeader"] [data-testid="stDecoration"],
    div[data-testid="stDecoration"] {{
      display: none !important;
    }}

    footer {{
      visibility: hidden !important;
    }}

    div[data-testid="stAppViewContainer"] {{
      overflow-x: clip !important;
    }}

    div[data-testid="stMainBlockContainer"],
    div[data-testid="stAppViewContainer"] .main .block-container {{
      padding-top: calc(var(--topbar-h) + 28px) !important;
      padding-bottom: 72px !important;
      max-width: 1280px !important;
      padding-left: 2.5rem !important;
      padding-right: 2.5rem !important;
    }}

    section[data-testid="stSidebar"] {{
      top: var(--topbar-h) !important;
      height: calc(100vh - var(--topbar-h)) !important;
      border-right: 1px solid var(--line) !important;
      box-shadow: none !important;
    }}

    section[data-testid="stSidebar"] > div {{
      padding-top: 8px !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {{
      height: 28px !important;
      padding-top: 4px !important;
    }}

    [data-testid="stExpandSidebarButton"],
    [data-testid="stSidebarCollapsedControl"] {{
      position: fixed !important;
      top: calc(var(--topbar-h) + 12px) !important;
      left: 12px !important;
      z-index: 10001 !important;
    }}

    #top-bar {{
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: var(--topbar-h);
      z-index: 9999;
      display: flex;
      align-items: center;
      background: rgba(255, 255, 255, 0.92);
      backdrop-filter: saturate(180%) blur(12px);
      border-bottom: 1px solid var(--line);
    }}

    #top-bar .inner {{
      width: 100%;
      padding: 0 24px;
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    #top-bar .logo {{
      width: 30px;
      height: 30px;
      border-radius: 8px;
      background: var(--primary);
      color: #fff;
      display: grid;
      place-items: center;
      font-size: 15px;
      font-weight: 800;
      flex-shrink: 0;
    }}

    #top-bar .brand {{
      font-size: 16px;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: var(--ink);
      white-space: nowrap;
    }}

    #top-bar .brand-sub {{
      font-size: 13px;
      color: var(--muted);
      white-space: nowrap;
      padding-left: 12px;
      margin-left: 2px;
      border-left: 1px solid var(--line);
    }}

    #top-bar .right {{
      margin-left: auto;
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    #top-bar .plan {{
      font-size: 12px;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: 999px;
      background: var(--bg-soft);
      color: var(--ink-2);
      border: 1px solid var(--line);
    }}

    #top-bar .plan.pro {{
      background: var(--primary-50);
      color: var(--primary-700);
      border-color: var(--primary-100);
    }}

    #top-bar .user {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      font-weight: 500;
      color: var(--ink-2);
    }}

    #top-bar .avatar {{
      width: 28px;
      height: 28px;
      border-radius: 999px;
      background: var(--bg-soft);
      border: 1px solid var(--line);
      display: grid;
      place-items: center;
      font-size: 12px;
      font-weight: 700;
      color: var(--muted);
    }}

    @media (max-width: 1024px) {{
      #top-bar .brand-sub {{
        display: none;
      }}

      div[data-testid="stMainBlockContainer"],
      div[data-testid="stAppViewContainer"] .main .block-container {{
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
      }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_top_hero(plan_label: str, user_label: str | None, is_pro: bool = False):
    plan_cls = "plan pro" if is_pro else "plan"
    if user_label:
        safe_user = html.escape(user_label)
        initial = html.escape(user_label[:1].upper())
        user_html = f'<div class="user"><div class="avatar">{initial}</div>{safe_user}</div>'
    else:
        user_html = '<div class="user">비회원</div>'
    st.markdown(
        f"""
        <div id="top-bar">
          <div class="inner">
            <div class="logo">P</div>
            <div class="brand">Pet Commerce Analytics</div>
            <div class="brand-sub">고객 이탈 예측 · CRM 대시보드</div>
            <div class="right">
              <span class="{plan_cls}">{html.escape(plan_label)}</span>
              {user_html}
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
