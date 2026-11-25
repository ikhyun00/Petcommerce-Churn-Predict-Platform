import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

PLOT_FONT = "Pretendard Variable, Pretendard, Apple SD Gothic Neo, Malgun Gothic, sans-serif"

COLORS = {
    "primary": "#4F46E5",
    "info": "#6366F1",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#E11D48",
    "text": "#111827",
    "subtext": "#6B7280",
    "grid": "#F1F2F4",
    "border": "#E5E7EB",
    "muted_bar": "#D1D5DB",
}

CHART_PALETTE = ["#4F46E5", "#818CF8", "#10B981", "#F59E0B", "#E11D48", "#94A3B8", "#C7D2FE"]
SEQ_SCALE = ["#E0E7FF", "#4F46E5"]
RISK_COLORS = {
    "즉시 관리": "#E11D48",
    "관리 필요": "#F59E0B",
    "관심 필요": "#818CF8",
    "안정": "#10B981",
}


def _apply_plot_theme(fig, height: int = 380):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=8, r=24, t=16, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=PLOT_FONT, size=12, color=COLORS["text"]),
        colorway=CHART_PALETTE,
        bargap=0.38,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12, color=COLORS["subtext"]),
            title_text="",
        ),
        hoverlabel=dict(
            bgcolor="white",
            bordercolor=COLORS["border"],
            font=dict(color=COLORS["text"], family=PLOT_FONT, size=12),
        ),
        xaxis=dict(showgrid=False, zeroline=False, linecolor=COLORS["border"], tickfont=dict(color=COLORS["subtext"]), title_font=dict(color=COLORS["subtext"], size=12)),
        yaxis=dict(showgrid=True, gridcolor=COLORS["grid"], zeroline=False, tickfont=dict(color=COLORS["subtext"]), title_font=dict(color=COLORS["subtext"], size=12)),
    )
    if any(getattr(t, "orientation", None) == "h" for t in fig.data):
        fig.update_xaxes(showgrid=True, gridcolor=COLORS["grid"], linecolor="rgba(0,0,0,0)")
        fig.update_yaxes(showgrid=False, linecolor=COLORS["border"])
    fig.update_traces(selector=dict(type="bar"), marker_line_width=0, textfont=dict(size=12, color=COLORS["text"]), cliponaxis=False)
    fig.update_traces(selector=dict(type="pie"), marker=dict(line=dict(color="white", width=2)), textfont=dict(size=12), insidetextorientation="horizontal")
    return fig


def section_header(title: str, desc: str | None = None, kicker: str | None = None):
    desc_html = f'<div class="section-desc">{desc}</div>' if desc else ''
    st.markdown(
        f"""
        <div class="section-head">
          <div class="section-title">{title}</div>
          {desc_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, foot: str = ""):
    st.markdown(
        f"""
        <div class="kpi-shell">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value" title="{value}">{value}</div>
          <div class="kpi-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_box(title: str, bullets: list[str], tone: str = "info"):
    tone_cls = tone if tone in {"warn", "danger", "success"} else ""
    bullet_html = ''.join(f'<li>{b}</li>' for b in bullets)
    st.markdown(
        f"""
        <div class="insight-panel {tone_cls}">
          <div class="insight-title">{title}</div>
          <ul class="bullet-list">{bullet_html}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def action_card(title: str, body: str, tag: str | None = None):
    tag_html = f'<span class="metric-pill">{tag}</span>' if tag else ''
    st.markdown(
        f"""
        <div class="action-card">
          <div class="action-head">
            <div class="action-title">{title}</div>
            {tag_html}
          </div>
          <div class="action-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chart_card(title: str, fig, desc: str | None = None, height: int = 380):
    fig = _apply_plot_theme(fig, height=height)
    desc_html = f'<div class="chart-desc">{desc}</div>' if desc else ''
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="chart-head">
              <div class="chart-title">{title}</div>
              {desc_html}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            theme=None,
            config={"displaylogo": False, "responsive": True, "displayModeBar": False},
        )


def bar_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None, orientation: str = "v"):
    fig = px.bar(
        df,
        x=x if orientation == "v" else y,
        y=y if orientation == "v" else x,
        color=color,
        orientation=orientation,
        color_discrete_sequence=CHART_PALETTE,
    )
    fig.update_traces(
        texttemplate="%{x}" if orientation == "h" else "%{y}",
        textposition="outside",
        cliponaxis=False,
    )
    return _apply_plot_theme(fig)


def donut_chart(df: pd.DataFrame, names: str, values: str):
    fig = px.pie(df, names=names, values=values, hole=0.58, color_discrete_sequence=CHART_PALETTE)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return _apply_plot_theme(fig)


def scatter_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None, size: str | None = None):
    fig = px.scatter(df, x=x, y=y, color=color, size=size, opacity=0.78, color_discrete_sequence=CHART_PALETTE)
    fig.update_traces(marker=dict(line=dict(width=0.5, color="white")))
    return _apply_plot_theme(fig)


def line_chart(df: pd.DataFrame, x: str, y: str, color: str | None = None):
    fig = px.line(df, x=x, y=y, color=color, markers=True, color_discrete_sequence=CHART_PALETTE)
    return _apply_plot_theme(fig)


def table_block(df: pd.DataFrame, caption: str | None = None, height: int = 320):
    if caption:
        st.markdown(f'<div class="table-caption">{caption}</div>', unsafe_allow_html=True)
    fit_height = 35 * (len(df) + 1) + 3
    st.dataframe(df, use_container_width=True, hide_index=True, height=min(height, fit_height))


def gauge_card(value: float, title: str, reference: float = 70):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": title, "font": {"size": 15, "color": COLORS["text"], "family": PLOT_FONT}},
            number={"suffix": "점", "font": {"size": 40, "color": COLORS["text"], "family": PLOT_FONT}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#D1D5DB", "tickfont": {"size": 12, "color": "#9CA3AF", "family": PLOT_FONT}},
                "bar": {"color": COLORS["primary"], "thickness": 0.6},
                "bgcolor": "white",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 40], "color": "#ECFDF5"},
                    {"range": [40, 70], "color": "#FFFBEB"},
                    {"range": [70, 100], "color": "#FEF2F2"},
                ],
                "threshold": {"line": {"color": COLORS["danger"], "width": 3}, "thickness": 0.85, "value": reference},
            },
        )
    )
    fig.update_layout(template="plotly_white", height=300, margin=dict(l=24, r=40, t=48, b=10), paper_bgcolor="rgba(0,0,0,0)", font=dict(family=PLOT_FONT))
    return fig


px.defaults.color_discrete_sequence = CHART_PALETTE
px.defaults.color_continuous_scale = SEQ_SCALE
