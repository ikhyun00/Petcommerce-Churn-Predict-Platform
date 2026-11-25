import streamlit as st


def apply_design_tokens():
    css = """
    <style>
    :root {
        --primary: #4F46E5;
        --primary-600: #4F46E5;
        --primary-700: #4338CA;
        --primary-100: #E0E7FF;
        --primary-50: #EEF2FF;
        --ink: #111827;
        --ink-2: #374151;
        --muted: #6B7280;
        --muted-2: #9CA3AF;
        --line: #E5E7EB;
        --line-2: #D1D5DB;
        --bg: #FFFFFF;
        --bg-card: #FFFFFF;
        --bg-soft: #F9FAFB;
        --success: #059669;
        --success-bg: #ECFDF5;
        --warning: #B45309;
        --warning-bg: #FFFBEB;
        --danger: #DC2626;
        --danger-bg: #FEF2F2;
        --info-bg: #EEF2FF;
        --radius-lg: 12px;
        --radius-md: 10px;
        --radius-sm: 8px;
        --shadow-xs: 0 1px 2px rgba(16, 24, 40, 0.04);
        --shadow-md: 0 4px 16px rgba(16, 24, 40, 0.06);
        --transition: 0.15s ease;
    }

    html, body, [class*="css"], .stApp, .stMarkdown, button, input, textarea, select {
        font-family: "Pretendard Variable", "Pretendard", -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }

    .stApp {
        color: var(--ink);
    }

    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        letter-spacing: -0.02em;
        color: var(--ink);
    }

    .stMarkdown h4 {
        font-size: 17px !important;
        font-weight: 700 !important;
        padding: 18px 0 6px !important;
    }

    .stMarkdown h5 {
        font-size: 15px !important;
        font-weight: 700 !important;
        padding: 10px 0 4px !important;
    }

    .stMarkdown h6 {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: var(--ink-2) !important;
    }

    /* ---------- page header ---------- */
    .page-eyebrow {
        font-size: 13px;
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 8px;
    }

    .page-title {
        font-size: 30px;
        line-height: 1.25;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: var(--ink);
        margin: 0;
        word-break: keep-all;
    }

    .page-subtitle {
        font-size: 15px;
        line-height: 1.7;
        color: var(--muted);
        margin: 8px 0 0 0;
        max-width: 760px;
        word-break: keep-all;
    }

    .page-head {
        margin-bottom: 20px;
    }

    .crumb {
        font-size: 13px;
        color: var(--muted);
        margin-bottom: 6px;
    }

    .crumb b {
        color: var(--ink-2);
        font-weight: 600;
    }

    /* ---------- home ---------- */
    .hero {
        padding: 8px 0 28px;
    }

    .hero-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        font-weight: 600;
        color: var(--primary-700);
        background: var(--primary-50);
        border-radius: 999px;
        padding: 4px 12px;
        margin-bottom: 16px;
    }

    .hero-title {
        font-size: 40px;
        line-height: 1.2;
        font-weight: 800;
        letter-spacing: -0.035em;
        color: var(--ink);
        word-break: keep-all;
    }

    .hero-title em {
        font-style: normal;
        color: var(--primary);
    }

    .hero-sub {
        margin-top: 14px;
        font-size: 16px;
        line-height: 1.75;
        color: var(--muted);
        max-width: 720px;
        word-break: keep-all;
    }

    .stepper {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin: 0 0 24px;
    }

    .step {
        display: flex;
        align-items: center;
        gap: 12px;
        background: var(--bg-card);
        border: 1px solid var(--line);
        border-radius: var(--radius-lg);
        padding: 14px 16px;
    }

    .step-num {
        flex-shrink: 0;
        width: 28px;
        height: 28px;
        border-radius: 999px;
        background: var(--bg-soft);
        color: var(--muted);
        display: grid;
        place-items: center;
        font-size: 13px;
        font-weight: 700;
    }

    .step-title {
        font-size: 14px;
        font-weight: 600;
        color: var(--ink);
    }

    .step-desc {
        font-size: 12.5px;
        color: var(--muted);
        margin-top: 1px;
    }

    .step.on {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px var(--primary-50);
    }

    .step.on .step-num {
        background: var(--primary);
        color: #fff;
    }

    .step.done .step-num {
        background: var(--primary-50);
        color: var(--primary-700);
    }

    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 16px;
        margin-top: 8px;
    }

    .feature {
        background: var(--bg-card);
        border: 1px solid var(--line);
        border-radius: var(--radius-lg);
        padding: 20px;
    }

    .feature-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: var(--primary-50);
        color: var(--primary);
        display: grid;
        place-items: center;
        margin-bottom: 14px;
    }

    .feature-title {
        font-size: 15px;
        font-weight: 700;
        color: var(--ink);
        margin-bottom: 6px;
    }

    .feature-desc {
        font-size: 13.5px;
        line-height: 1.7;
        color: var(--muted);
        word-break: keep-all;
    }

    .card-title {
        font-size: 18px;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--ink);
    }

    .card-desc {
        font-size: 14px;
        line-height: 1.65;
        color: var(--muted);
        margin: 6px 0 16px;
        word-break: keep-all;
    }

    .card-tag {
        display: inline-block;
        font-size: 12px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 999px;
        margin-bottom: 12px;
        background: var(--primary-50);
        color: var(--primary-700);
    }

    .card-tag.green {
        background: var(--success-bg);
        color: var(--success);
    }

    .hint {
        display: flex;
        gap: 8px;
        align-items: flex-start;
        margin-top: 12px;
        font-size: 13px;
        line-height: 1.6;
        color: var(--muted);
    }

    .hint::before {
        content: "i";
        flex-shrink: 0;
        width: 16px;
        height: 16px;
        margin-top: 2px;
        border-radius: 999px;
        background: var(--bg-soft);
        color: var(--muted);
        font-size: 11px;
        font-weight: 700;
        display: grid;
        place-items: center;
    }

    /* ---------- section ---------- */
    .section-kicker {
        display: none;
    }

    .section-head {
        margin: 36px 0 14px;
    }

    .section-title {
        font-size: 20px;
        line-height: 1.35;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--ink);
        margin: 0;
        word-break: keep-all;
    }

    .section-desc {
        margin-top: 4px;
        color: var(--muted);
        font-size: 14px;
        line-height: 1.65;
        max-width: 860px;
        word-break: keep-all;
    }

    .section-gap {
        height: 8px;
    }

    /* ---------- KPI ---------- */
    .kpi-shell {
        background: var(--bg-card);
        border: 1px solid var(--line);
        border-radius: var(--radius-lg);
        padding: 18px 20px;
        min-height: 124px;
        margin-bottom: 4px;
    }

    .kpi-shell .kpi-label {
        font-size: 13px;
        font-weight: 500;
        color: var(--muted);
    }

    .kpi-shell .kpi-value {
        margin-top: 8px;
        font-size: 28px;
        line-height: 1.2;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: var(--ink);
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .kpi-shell .kpi-foot {
        margin-top: 6px;
        font-size: 12.5px;
        line-height: 1.5;
        color: var(--muted);
    }

    /* ---------- insight / action ---------- */
    .insight-panel {
        background: var(--bg-card);
        border: 1px solid var(--line);
        border-radius: var(--radius-lg);
        padding: 18px 20px;
        margin: 12px 0 4px;
    }

    .insight-panel.warn { background: var(--warning-bg); border-color: #FDE68A; }
    .insight-panel.danger { background: var(--danger-bg); border-color: #FECACA; }
    .insight-panel.success { background: var(--success-bg); border-color: #A7F3D0; }

    .insight-title {
        font-size: 15px;
        font-weight: 700;
        color: var(--ink);
    }

    .bullet-list {
        list-style: none;
        margin: 8px 0 0 0;
        padding: 0;
    }

    .bullet-list li {
        position: relative;
        padding: 6px 0 6px 16px;
        color: var(--ink-2);
        font-size: 14px;
        line-height: 1.65;
        word-break: keep-all;
    }

    .bullet-list li::before {
        content: "";
        position: absolute;
        left: 2px;
        top: 15px;
        width: 5px;
        height: 5px;
        border-radius: 999px;
        background: var(--primary);
    }

    .metric-pill {
        display: inline-flex;
        align-items: center;
        padding: 3px 9px;
        border-radius: 6px;
        background: var(--primary-50);
        color: var(--primary-700);
        font-size: 12px;
        font-weight: 600;
        white-space: nowrap;
    }

    .action-card {
        background: var(--bg-card);
        border: 1px solid var(--line);
        border-radius: var(--radius-lg);
        padding: 16px 18px;
        margin-bottom: 10px;
        transition: border-color var(--transition), box-shadow var(--transition);
    }

    .action-card:hover {
        border-color: var(--line-2);
        box-shadow: var(--shadow-md);
    }

    .action-head {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        align-items: center;
        margin-bottom: 4px;
    }

    .action-title {
        font-size: 15px;
        font-weight: 600;
        color: var(--ink);
        line-height: 1.45;
    }

    .action-body {
        color: var(--muted);
        font-size: 13.5px;
        line-height: 1.65;
        word-break: keep-all;
    }

    /* ---------- chart / table ---------- */
    .chart-head {
        margin-bottom: 2px;
    }

    .chart-title {
        font-size: 15px;
        font-weight: 700;
        color: var(--ink);
        line-height: 1.4;
    }

    .chart-desc {
        margin-top: 2px;
        color: var(--muted);
        font-size: 13px;
        line-height: 1.55;
        word-break: keep-all;
    }

    .table-caption {
        font-size: 14px;
        color: var(--ink-2);
        font-weight: 600;
        margin: 10px 0 8px;
    }

    /* ---------- sidebar ---------- */
    .side-section-title {
        font-size: 12px;
        font-weight: 600;
        color: var(--muted);
        margin: 18px 2px 6px;
    }

    .side-section-title:first-child {
        margin-top: 4px;
    }

    .sidebar-note {
        color: var(--muted);
        font-size: 13px;
        line-height: 1.6;
        padding: 2px 2px 4px;
    }

    .side-user {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 12px;
        border: 1px solid var(--line);
        border-radius: var(--radius-md);
        margin-bottom: 8px;
    }

    .side-user .avatar {
        width: 32px;
        height: 32px;
        border-radius: 999px;
        background: var(--primary-50);
        color: var(--primary-700);
        display: grid;
        place-items: center;
        font-weight: 700;
        font-size: 13px;
    }

    .side-user .name {
        font-size: 14px;
        font-weight: 600;
        color: var(--ink);
    }

    .side-user .meta {
        font-size: 12px;
        color: var(--muted);
    }

    .side-guide {
        margin-top: 8px;
        padding: 14px;
        border-radius: var(--radius-md);
        background: var(--bg-soft);
        font-size: 13px;
        line-height: 1.7;
        color: var(--muted);
    }

    .side-guide b {
        display: block;
        color: var(--ink-2);
        font-weight: 600;
        margin-bottom: 2px;
    }

    section[data-testid="stSidebar"] .stButton > button {
        min-height: 38px !important;
        font-size: 14px !important;
    }

    section[data-testid="stSidebar"] [class*="st-key-recent_run_"] button,
    section[data-testid="stSidebar"] [class*="st-key-nav_"] button {
        justify-content: flex-start !important;
        border-color: transparent !important;
        background: transparent !important;
        box-shadow: none !important;
        font-weight: 500 !important;
        color: var(--ink-2) !important;
        padding-left: 10px !important;
    }

    section[data-testid="stSidebar"] [class*="st-key-recent_run_"] button > div,
    section[data-testid="stSidebar"] [class*="st-key-nav_"] button > div {
        justify-content: flex-start !important;
        width: 100%;
    }

    section[data-testid="stSidebar"] [class*="st-key-recent_run_"] button:hover,
    section[data-testid="stSidebar"] [class*="st-key-nav_"] button:hover {
        background: var(--bg-soft) !important;
    }

    section[data-testid="stSidebar"] [class*="st-key-recent_run_"] button p {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        text-align: left;
    }

    section[data-testid="stSidebar"] [class*="st-key-recent_run_on_"] button {
        background: var(--primary-50) !important;
        color: var(--primary-700) !important;
        font-weight: 600 !important;
    }

    /* ---------- banners ---------- */
    .info-banner,
    .warn-banner,
    .danger-banner,
    .success-banner {
        border-radius: var(--radius-md);
        padding: 12px 14px;
        font-size: 14px;
        line-height: 1.65;
        margin: 10px 0;
        border: 1px solid;
        word-break: keep-all;
    }

    .info-banner { background: var(--info-bg); border-color: var(--primary-100); color: var(--ink-2); }
    .warn-banner { background: var(--warning-bg); border-color: #FDE68A; color: #92400E; }
    .danger-banner { background: var(--danger-bg); border-color: #FECACA; color: #991B1B; }
    .success-banner { background: var(--success-bg); border-color: #A7F3D0; color: #065F46; }

    .card-muted {
        background: var(--bg-soft);
        border-radius: var(--radius-md);
        padding: 14px 16px;
    }

    .label {
        font-size: 12px;
        font-weight: 600;
        color: var(--muted);
        margin-bottom: 6px;
    }

    .hr {
        height: 1px;
        margin: 14px 0;
        background: var(--line);
    }

    /* ---------- mapping step ---------- */
    .step-section-label {
        flex-shrink: 0;
        min-width: 26px;
        height: 26px;
        padding: 0 8px;
        border-radius: 999px;
        background: var(--primary-50);
        color: var(--primary-700);
        font-size: 13px;
        font-weight: 700;
        display: grid;
        place-items: center;
    }

    .step-section-title {
        font-size: 19px;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--ink);
    }

    .step-section-desc {
        font-size: 14px;
        color: var(--muted);
        line-height: 1.65;
        margin: 4px 0 0 36px;
    }

    .quality-header-card {
        border-radius: var(--radius-lg) !important;
        padding: 20px 22px !important;
        margin: 8px 0 16px !important;
        box-shadow: none !important;
    }

    /* ---------- loading ---------- */
    .loading-overlay {
        position: fixed;
        inset: 0;
        z-index: 99999;
        background: rgba(17, 24, 39, 0.28);
        backdrop-filter: blur(4px);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .loading-modal {
        width: min(400px, 92vw);
        background: var(--bg-card);
        border-radius: 16px;
        box-shadow: 0 24px 60px rgba(17, 24, 39, 0.18);
        padding: 28px 24px 24px;
        text-align: center;
    }

    .loading-badge {
        display: none;
    }

    .loading-title {
        font-size: 20px;
        font-weight: 700;
        color: var(--ink);
    }

    .loading-desc {
        margin-top: 6px;
        font-size: 14px;
        color: var(--muted);
        line-height: 1.6;
    }

    .loading-dots {
        margin: 18px auto 0;
        display: flex;
        justify-content: center;
        gap: 6px;
    }

    .loading-dots span {
        width: 8px;
        height: 8px;
        border-radius: 999px;
        background: var(--primary);
        animation: loading-bounce 1.2s infinite ease-in-out;
    }

    .loading-dots span:nth-child(2) { animation-delay: 0.15s; }
    .loading-dots span:nth-child(3) { animation-delay: 0.30s; }

    @keyframes loading-bounce {
        0%, 80%, 100% { transform: scale(0.7); opacity: 0.4; }
        40% { transform: scale(1); opacity: 1; }
    }

    /* ---------- streamlit widgets ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stForm"] {
        background: var(--bg-card);
        border-radius: var(--radius-lg) !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] {
        background: transparent;
    }

    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button,
    div[data-testid="stPopover"] button {
        border-radius: var(--radius-sm) !important;
        min-height: 40px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        box-shadow: var(--shadow-xs) !important;
        transition: background var(--transition), border-color var(--transition) !important;
    }

    .stButton > button[kind="secondary"],
    .stDownloadButton > button[kind="secondary"],
    .stFormSubmitButton > button[kind="secondaryFormSubmit"] {
        background: #FFFFFF !important;
        border: 1px solid var(--line-2) !important;
        color: var(--ink-2) !important;
    }

    .stButton > button[kind="secondary"]:hover,
    .stDownloadButton > button[kind="secondary"]:hover,
    .stFormSubmitButton > button[kind="secondaryFormSubmit"]:hover {
        background: var(--bg-soft) !important;
        border-color: var(--line-2) !important;
        color: var(--ink) !important;
    }

    .stButton > button[kind="primary"],
    .stDownloadButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primaryFormSubmit"] {
        background: var(--primary) !important;
        border: 1px solid var(--primary) !important;
        color: #FFFFFF !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stDownloadButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button[kind="primaryFormSubmit"]:hover {
        background: var(--primary-700) !important;
        border-color: var(--primary-700) !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 28px;
        overflow-x: auto;
        scrollbar-width: none;
        border-bottom: 1px solid var(--line);
        margin-bottom: 8px;
    }

    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
        display: none;
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        padding: 0;
        background: transparent !important;
        white-space: nowrap;
    }

    .stTabs [data-baseweb="tab"] p {
        font-size: 15px !important;
        font-weight: 500;
        color: var(--muted);
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] p {
        color: var(--ink);
        font-weight: 700;
    }

    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }

    div[data-testid="stExpander"] details {
        border-radius: var(--radius-md) !important;
        border-color: var(--line) !important;
        background: var(--bg-card);
    }

    div[data-testid="stExpander"] summary p {
        font-weight: 600;
    }

    div[data-testid="stAlert"] > div {
        border-radius: var(--radius-md) !important;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: var(--radius-md);
        overflow: hidden;
    }

    [data-testid="stFileUploaderDropzone"] {
        border: 1.5px dashed var(--line-2) !important;
        border-radius: var(--radius-md) !important;
        background: var(--bg-soft) !important;
        padding: 22px 18px !important;
    }

    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--primary) !important;
        background: var(--primary-50) !important;
    }

    div[data-testid="stDialog"] div[role="dialog"] {
        border-radius: 16px !important;
    }

    @media (max-width: 1100px) {
        .feature-grid,
        .stepper {
            grid-template-columns: 1fr;
        }

        .hero-title {
            font-size: 32px;
        }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
