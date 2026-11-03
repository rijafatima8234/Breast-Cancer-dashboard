"""CareLens Analytics — premium interactive breast cancer EDA platform."""

from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Breast Cancer Analytics | CareLens",
    page_icon="✚",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).with_name("Breast_Cancer.csv")

COLORS = {
    "background": "#F5F6FA",
    "sidebar": "#111827",
    "navy": "#172554",
    "purple": "#7657E8",
    "pink": "#E879A5",
    "teal": "#20B8A5",
    "surface": "#FFFFFF",
    "text": "#1E293B",
    "muted": "#8490A5",
    "border": "#E8ECF3",
    "soft_purple": "#F2EFFF",
    "soft_pink": "#FFF0F6",
}

CHART_COLORS = ["#7657E8", "#20B8A5", "#E879A5", "#172554", "#D6A44A", "#6B8EBD"]
STATUS_COLORS = {"Alive": COLORS["teal"], "Dead": COLORS["pink"]}
FILTER_KEYS = (
    "age_range",
    "stage_filter",
    "status_filter",
    "race_filter",
    "estrogen_filter",
    "marital_filter",
)
NAVIGATION = {
    "Overview": "◈",
    "Demographic Analysis": "◌",
    "Clinical Analysis": "✚",
    "Survival Analysis": "↗",
    "Insights & Recommendations": "✦",
    "Dataset Explorer": "▦",
}

px.defaults.color_discrete_sequence = CHART_COLORS


def inject_styles() -> None:
    """Set the premium visual system using Streamlit-compatible CSS only."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

        :root {{
          --canvas: {COLORS['background']}; --surface: {COLORS['surface']};
          --sidebar: {COLORS['sidebar']}; --navy: {COLORS['navy']};
          --purple: {COLORS['purple']}; --pink: {COLORS['pink']};
          --teal: {COLORS['teal']}; --ink: {COLORS['text']};
          --muted: {COLORS['muted']}; --border: {COLORS['border']};
        }}
        .stApp {{ background: var(--canvas); color: var(--ink); }}
        .stApp, .stApp button, .stApp input, .stApp textarea {{ font-family: 'DM Sans', Arial, sans-serif; }}
        #MainMenu, footer, header {{ visibility: hidden; }}
        .block-container {{ max-width: 1540px; padding: 1.6rem 2.35rem 2.2rem; }}
        h1, h2, h3 {{ color: var(--navy); font-family: 'Manrope', 'DM Sans', Arial, sans-serif; letter-spacing: -.035em; }}
        h2 {{ font-size: 1.35rem !important; margin: 1.7rem 0 .22rem !important; }}
        h3 {{ font-size: 1rem !important; }}
        [data-testid="stSidebar"] {{ background: var(--sidebar); border-right: 0; }}
        [data-testid="stSidebar"] > div:first-child {{ background: linear-gradient(180deg, #111827 0%, #172554 100%); }}
        [data-testid="stSidebar"] * {{ color: #F8FAFC; }}
        [data-testid="stSidebar"] .stMarkdown p {{ color: #C2CBDC; }}
        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] [data-baseweb="input"] > div {{
          color: #F8FAFC; background: rgba(255,255,255,.075); border-color: rgba(255,255,255,.12);
        }}
        [data-testid="stSidebar"] [data-baseweb="select"] svg {{ fill: #F8FAFC; }}
        [data-testid="stSidebar"] [data-baseweb="tag"] {{ background: rgba(118,87,232,.35); }}
        [data-testid="stSidebar"] [data-baseweb="slider"] div {{ color: var(--purple); }}
        [data-testid="stSidebar"] label[data-baseweb="radio"] {{
          border-radius: 10px; padding: .45rem .55rem; margin: .07rem 0; transition: background .18s ease, transform .18s ease;
        }}
        [data-testid="stSidebar"] label[data-baseweb="radio"]:hover {{ background: rgba(255,255,255,.07); transform: translateX(2px); }}
        [data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) {{
          background: linear-gradient(100deg, rgba(118,87,232,.98), rgba(150,92,219,.82));
          box-shadow: 0 8px 20px rgba(72,43,174,.32);
        }}
        [data-testid="stSidebar"] .stButton > button {{ background: rgba(255,255,255,.09); border: 1px solid rgba(255,255,255,.16); color: #F8FAFC; }}
        [data-testid="stSidebar"] .stButton > button:hover {{ background: rgba(232,121,165,.24); border-color: rgba(232,121,165,.5); }}
        [data-testid="stSidebar"] .stDownloadButton > button {{ background: linear-gradient(100deg, #7657E8, #9569E6); color: white; border: 0; }}
        [data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,.10); }}
        .brand {{ padding: .45rem .1rem 1.15rem; }}
        .brand-symbol {{
          width: 42px; height: 42px; display: grid; place-items: center; border-radius: 13px;
          color: white; font-size: 1.25rem; font-weight: 800; background: linear-gradient(135deg, #7657E8, #E879A5);
          box-shadow: 0 8px 20px rgba(118,87,232,.35);
        }}
        .brand-title {{ color: white; font: 700 1.08rem 'Manrope', sans-serif; margin: .7rem 0 .18rem; letter-spacing: -.02em; }}
        .brand-subtitle {{ color: #AEBBD0; font-size: .76rem; margin: 0; line-height: 1.45; }}
        .sidebar-label {{ color: #AEBBD0; font-size: .7rem; font-weight: 700; letter-spacing: .11em; text-transform: uppercase; margin: .2rem 0 .48rem; }}
        .sidebar-data {{ background: rgba(255,255,255,.055); border: 1px solid rgba(255,255,255,.085); border-radius: 12px; padding: .72rem .75rem; margin-top: .45rem; }}
        .sidebar-data strong {{ display: block; color: white; font-size: .9rem; margin-bottom: .15rem; }}
        .sidebar-data span {{ display: block; color: #AEBBD0; font-size: .72rem; line-height: 1.45; }}
        .sidebar-footer {{ color: #8190AA; font-size: .7rem; padding: .35rem .15rem 0; line-height: 1.45; }}
        .app-header {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; padding: .25rem 0 1.35rem; }}
        .eyebrow {{ color: var(--purple); font-size: .7rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; margin-bottom: .35rem; }}
        .app-header h1 {{ font-size: clamp(1.8rem, 3vw, 2.45rem); margin: 0; line-height: 1.14; }}
        .app-header p {{ color: var(--muted); font-size: .95rem; margin: .42rem 0 0; }}
        .data-chip {{ flex: 0 0 auto; display: flex; gap: .65rem; align-items: center; background: white; border: 1px solid var(--border); border-radius: 14px; padding: .72rem .85rem; box-shadow: 0 5px 15px rgba(23,37,84,.045); }}
        .data-chip-icon {{ width: 29px; height: 29px; display: grid; place-items: center; color: var(--purple); border-radius: 9px; background: #F2EFFF; font-size: .9rem; }}
        .data-chip strong {{ display: block; color: var(--ink); font-size: .78rem; }}
        .data-chip span {{ display: block; color: var(--muted); font-size: .7rem; margin-top: .08rem; }}
        .hero {{ position: relative; overflow: hidden; border-radius: 22px; min-height: 190px; box-sizing: border-box; padding: 2.05rem 2.25rem; color: white; background: linear-gradient(118deg, #172554 0%, #5540BD 58%, #A15ACC 100%); box-shadow: 0 16px 34px rgba(78,57,173,.18); margin-bottom: 1.4rem; }}
        .hero:before {{ content: ''; position: absolute; width: 260px; height: 260px; border-radius: 50%; background: rgba(255,255,255,.09); right: -72px; top: -120px; }}
        .hero:after {{ content: ''; position: absolute; width: 165px; height: 165px; border: 1px solid rgba(255,255,255,.20); border-radius: 50%; right: 130px; bottom: -90px; }}
        .hero-badge {{ display: inline-block; border: 1px solid rgba(255,255,255,.24); background: rgba(255,255,255,.12); padding: .33rem .65rem; border-radius: 999px; color: #F8F6FF; font-size: .7rem; font-weight: 700; letter-spacing: .055em; position: relative; z-index: 1; }}
        .hero h2 {{ color: white !important; font-size: clamp(1.55rem, 2.5vw, 2.2rem) !important; margin: .85rem 0 .35rem !important; max-width: 650px; position: relative; z-index: 1; }}
        .hero p {{ color: #EBE9FF; max-width: 650px; line-height: 1.55; margin: 0; font-size: .94rem; position: relative; z-index: 1; }}
        .hero-cohort {{ color: #F5D9E8; font-size: .76rem; margin-top: .9rem; position: relative; z-index: 1; }}
        .section-intro {{ color: var(--muted); margin: 0 0 1.05rem; font-size: .9rem; line-height: 1.5; }}
        .filter-summary {{ display: inline-flex; gap: .45rem; align-items: center; color: #6652C0; font-size: .75rem; font-weight: 700; background: #F2EFFF; border: 1px solid #E4DDFE; border-radius: 999px; padding: .38rem .7rem; margin: 0 0 .75rem; }}
        .filter-summary b {{ color: #4F3CA8; }}
        .kpi-card {{ min-height: 139px; box-sizing: border-box; position: relative; overflow: hidden; background: white; border: 1px solid var(--border); border-radius: 16px; padding: 1rem 1.05rem; box-shadow: 0 7px 22px rgba(23,37,84,.055); transition: transform .18s ease, box-shadow .18s ease; }}
        .kpi-card:hover {{ transform: translateY(-3px); box-shadow: 0 13px 25px rgba(23,37,84,.095); }}
        .kpi-icon {{ width: 38px; height: 38px; display: grid; place-items: center; border-radius: 12px; font-size: 1rem; font-weight: 800; }}
        .kpi-icon.purple {{ color: #684BD7; background: linear-gradient(135deg, #EFEAFF, #E1D9FF); }}
        .kpi-icon.teal {{ color: #138B7C; background: linear-gradient(135deg, #DDF8F3, #C8F2E9); }}
        .kpi-icon.pink {{ color: #C85883; background: linear-gradient(135deg, #FFE9F1, #FCD7E5); }}
        .kpi-icon.navy {{ color: #294177; background: linear-gradient(135deg, #E9EEFC, #DCE5FD); }}
        .kpi-label {{ color: var(--muted); font-size: .72rem; font-weight: 700; letter-spacing: .065em; text-transform: uppercase; margin-top: .7rem; }}
        .kpi-value {{ color: var(--navy); font: 800 1.7rem 'Manrope', sans-serif; letter-spacing: -.04em; margin: .1rem 0 .2rem; }}
        .kpi-detail {{ color: var(--muted); font-size: .75rem; }}
        .kpi-detail strong {{ color: var(--teal); font-weight: 700; }}
        .chart-note {{ color: var(--muted); min-height: 28px; font-size: .77rem; line-height: 1.4; margin: .1rem .15rem .38rem; }}
        [data-testid="stPlotlyChart"] {{ background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: .24rem .45rem; box-shadow: 0 7px 20px rgba(23,37,84,.045); }}
        [data-testid="stDataFrame"] {{ background: white; border: 1px solid var(--border); border-radius: 14px; overflow: hidden; }}
        .highlight-card {{ min-height: 112px; box-sizing: border-box; background: white; border: 1px solid var(--border); border-radius: 14px; padding: .95rem; box-shadow: 0 5px 16px rgba(23,37,84,.035); }}
        .highlight-label {{ color: var(--muted); font-size: .68rem; letter-spacing: .07em; text-transform: uppercase; font-weight: 800; }}
        .highlight-value {{ color: var(--navy); font: 800 1.18rem 'Manrope', sans-serif; letter-spacing: -.03em; margin-top: .38rem; }}
        .highlight-detail {{ color: var(--muted); font-size: .75rem; line-height: 1.4; margin-top: .22rem; }}
        .insight-card, .recommendation-card {{ height: 100%; min-height: 194px; box-sizing: border-box; background: white; border: 1px solid var(--border); border-radius: 16px; padding: 1.1rem; box-shadow: 0 6px 18px rgba(23,37,84,.045); transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease; }}
        .insight-card:hover, .recommendation-card:hover {{ transform: translateY(-4px); border-color: #DCD5FF; box-shadow: 0 15px 28px rgba(65,49,150,.11); }}
        .insight-accent {{ width: 34px; height: 4px; border-radius: 99px; background: linear-gradient(90deg, var(--purple), var(--pink)); }}
        .insight-icon {{ width: 40px; height: 40px; display: grid; place-items: center; border-radius: 12px; background: #F2EFFF; color: var(--purple); font-size: 1rem; font-weight: 800; margin-top: .85rem; }}
        .insight-card h3, .recommendation-card h3 {{ color: var(--navy); font: 700 .96rem 'Manrope', sans-serif; margin: .73rem 0 .38rem !important; }}
        .insight-card p, .recommendation-card p {{ color: var(--muted); font-size: .82rem; line-height: 1.54; margin: 0; }}
        .recommendation-card {{ min-height: 176px; border-left: 4px solid var(--purple); }}
        .recommendation-card.important {{ border-left-color: var(--pink); }}
        .recommendation-number {{ display: grid; place-items: center; width: 28px; height: 28px; background: #F2EFFF; border-radius: 9px; color: var(--purple); font-size: .76rem; font-weight: 800; }}
        .recommendation-card.important .recommendation-number {{ background: #FFF0F6; color: #C85883; }}
        .explorer-stat {{ background: white; border: 1px solid var(--border); border-radius: 13px; padding: .82rem .9rem; }}
        .explorer-stat span {{ display: block; color: var(--muted); font-size: .68rem; text-transform: uppercase; font-weight: 800; letter-spacing: .06em; }}
        .explorer-stat strong {{ display: block; color: var(--navy); font: 800 1.2rem 'Manrope', sans-serif; margin-top: .24rem; }}
        .stButton > button, .stDownloadButton > button {{ border-radius: 10px; font-weight: 700; transition: transform .16s ease, box-shadow .16s ease; }}
        .stButton > button:hover, .stDownloadButton > button:hover {{ transform: translateY(-1px); box-shadow: 0 6px 14px rgba(23,37,84,.10); }}
        [data-testid="stExpander"] {{ background: white; border: 1px solid var(--border); border-radius: 13px; }}
        .footer {{ border-top: 1px solid var(--border); color: var(--muted); text-align: center; font-size: .72rem; letter-spacing: .02em; margin-top: 2rem; padding: 1.15rem 0 .2rem; }}
        @media (max-width: 820px) {{
          .block-container {{ padding: 1.05rem .9rem 1.8rem; }}
          .app-header {{ display: block; }} .data-chip {{ display: inline-flex; margin-top: .85rem; }}
          .hero {{ padding: 1.5rem; min-height: 170px; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    """Load source data without dropping records or changing source calculations."""
    data = pd.read_csv(path)
    data.columns = data.columns.str.strip()

    numeric_columns = [
        "Age",
        "Tumor Size",
        "Regional Node Examined",
        "Reginol Node Positive",
        "Survival Months",
    ]
    for column in numeric_columns:
        if column in data:
            data[column] = pd.to_numeric(data[column], errors="coerce")

    for column in data.columns:
        if str(data[column].dtype) in {"object", "string"}:
            data[column] = data[column].astype("string").str.strip().fillna("Unknown")
    return data


def format_number(value: float | int | None, decimals: int = 0) -> str:
    if value is None or pd.isna(value):
        return "--"
    return f"{value:,.{decimals}f}"


def category_options(series: pd.Series) -> list[str]:
    """Return a stable, data-driven category order for filters and charts."""
    return sorted(series.dropna().astype(str).unique().tolist(), key=lambda item: (len(item), item))


def with_age_groups(frame: pd.DataFrame) -> pd.DataFrame:
    """Add data-derived decade cohorts for readable demographic comparisons."""
    if "Age" not in frame:
        return frame
    result = frame.copy()
    decade_start = (result["Age"] // 10 * 10).astype("Int64")
    result["Age Group"] = decade_start.astype("string") + "s"
    result.loc[result["Age"].isna(), "Age Group"] = "Unknown"
    return result


def reset_filters() -> None:
    for key in FILTER_KEYS:
        st.session_state.pop(key, None)


def source_updated_label() -> str:
    try:
        return datetime.fromtimestamp(DATA_PATH.stat().st_mtime).strftime("%d %b %Y")
    except OSError:
        return "Unavailable"


def filtered_label(frame: pd.DataFrame, source: pd.DataFrame) -> str:
    if len(frame) == len(source):
        return "Full cohort selected"
    return f"{len(frame):,} of {len(source):,} patients selected"


def sidebar_and_filters(data: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    """Render one filter panel that drives every analytical page."""
    with st.sidebar:
        st.markdown(
            """
            <div class="brand">
                <div class="brand-symbol">✚</div>
                <div class="brand-title">CareLens Analytics</div>
                <p class="brand-subtitle">Healthcare exploratory intelligence</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        page = st.radio(
            "Navigation",
            list(NAVIGATION),
            format_func=lambda item: f"{NAVIGATION[item]}  {item}",
            label_visibility="collapsed",
        )
        st.markdown("---")
        st.markdown("<div class='sidebar-label'>Cohort controls</div>", unsafe_allow_html=True)

        active = data.copy()
        if "Age" in data and data["Age"].notna().any():
            lower, upper = int(data["Age"].min()), int(data["Age"].max())
            if lower < upper:
                age_range = st.slider("Age range", lower, upper, (lower, upper), key="age_range")
                active = active[active["Age"].between(age_range[0], age_range[1], inclusive="both")]

        filter_specs = [
            ("6th Stage", "Cancer stage", "stage_filter"),
            ("Status", "Patient status", "status_filter"),
            ("Race", "Race", "race_filter"),
            ("Estrogen Status", "Estrogen status", "estrogen_filter"),
            ("Marital Status", "Marital status", "marital_filter"),
        ]
        for column, label, key in filter_specs:
            if column in data:
                options = category_options(data[column])
                selected = st.multiselect(label, options, default=options, key=key)
                if selected:
                    active = active[active[column].isin(selected)]

        st.markdown(
            f"<div class='sidebar-data'><strong>{len(active):,} matching patients</strong><span>{len(active) / len(data) * 100:.1f}% of source cohort</span></div>",
            unsafe_allow_html=True,
        )
        if st.button("Clear all filters", width="stretch"):
            reset_filters()
            st.rerun()

        st.markdown("---")
        st.markdown("<div class='sidebar-label'>Dataset</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='sidebar-data'><strong>{len(data):,} patients · {len(data.columns)} fields</strong><span>Source updated {source_updated_label()}</span></div>",
            unsafe_allow_html=True,
        )
        st.download_button(
            "Download filtered CSV",
            data=active.to_csv(index=False).encode("utf-8"),
            file_name="carelens_filtered_breast_cancer_data.csv",
            mime="text/csv",
            width="stretch",
        )
        st.markdown("<p class='sidebar-footer'>CareLens Analytics<br>Exploratory data analysis only</p>", unsafe_allow_html=True)
    return page, active


def render_header(page: str, frame: pd.DataFrame, source: pd.DataFrame) -> None:
    """Render data-grounded application context at the top of every page."""
    st.markdown(
        f"""
        <section class="app-header">
          <div>
            <div class="eyebrow">Healthcare analytics platform · {escape(page)}</div>
            <h1>Breast Cancer Analytics</h1>
            <p>Explore patient demographics, clinical characteristics and survival patterns.</p>
          </div>
          <div class="data-chip">
            <div class="data-chip-icon">▦</div>
            <div><strong>{len(frame):,} active records</strong><span>{len(source.columns)} fields · updated {escape(source_updated_label())}</span></div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_overview_hero(frame: pd.DataFrame, source: pd.DataFrame) -> None:
    st.markdown(
        f"""
        <section class="hero">
          <span class="hero-badge">CARE LENS · DATA-DRIVEN VIEW</span>
          <h2>Bring the patient cohort into focus.</h2>
          <p>Interactively examine the demographic, clinical, and recorded survival characteristics in the selected breast cancer cohort.</p>
          <div class="hero-cohort">{escape(filtered_label(frame, source))}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def style_figure(figure: go.Figure, title: str, height: int = 350) -> go.Figure:
    figure.update_layout(
        title={"text": title, "x": 0.025, "xanchor": "left", "font": {"family": "Manrope", "size": 15, "color": COLORS["navy"]}},
        height=height,
        margin={"l": 18, "r": 18, "t": 54, "b": 22},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "DM Sans, Arial, sans-serif", "color": COLORS["text"], "size": 12},
        colorway=CHART_COLORS,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1, "title": {"text": ""}},
        hoverlabel={"bgcolor": COLORS["navy"], "font": {"color": "white"}, "bordercolor": COLORS["navy"]},
    )
    figure.update_xaxes(showgrid=False, zeroline=False, linecolor=COLORS["border"], tickfont={"color": COLORS["muted"]})
    figure.update_yaxes(gridcolor="#EEF1F6", zeroline=False, linecolor=COLORS["border"], tickfont={"color": COLORS["muted"]})
    return figure


def show_chart(figure: go.Figure, title: str, description: str, height: int = 350) -> None:
    st.markdown(f"<div class='chart-note'>{escape(description)}</div>", unsafe_allow_html=True)
    st.plotly_chart(
        style_figure(figure, title, height),
        width="stretch",
        config={"displaylogo": False, "responsive": True},
    )


def empty_state() -> None:
    st.warning("No records match the active filters. Clear or broaden the cohort controls to continue.")


def kpi_card(icon: str, color: str, label: str, value: str, detail: str) -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-icon {escape(color)}">{escape(icon)}</div>
          <div class="kpi-label">{escape(label)}</div>
          <div class="kpi-value">{escape(value)}</div>
          <div class="kpi-detail">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(frame: pd.DataFrame, source: pd.DataFrame) -> None:
    alive = int((frame.get("Status", pd.Series(dtype="string")) == "Alive").sum())
    deceased = int((frame.get("Status", pd.Series(dtype="string")) == "Dead").sum())
    average_survival = frame["Survival Months"].mean() if "Survival Months" in frame else None
    selected_percent = len(frame) / len(source) * 100 if len(source) else 0
    alive_percent = alive / len(frame) * 100 if len(frame) else 0
    deceased_percent = deceased / len(frame) * 100 if len(frame) else 0

    cards = st.columns(4, gap="large")
    with cards[0]:
        kpi_card("◉", "purple", "Total patients", format_number(len(frame)), f"<strong>{selected_percent:.1f}%</strong> of source cohort")
    with cards[1]:
        kpi_card("+", "teal", "Alive patients", format_number(alive), f"<strong>{alive_percent:.1f}%</strong> of active cohort")
    with cards[2]:
        kpi_card("−", "pink", "Deceased patients", format_number(deceased), f"<strong>{deceased_percent:.1f}%</strong> of active cohort")
    with cards[3]:
        kpi_card("↗", "navy", "Average survival", f"{format_number(average_survival, 1)} mo", "Across matching patient records")


def highlight_card(label: str, value: str, detail: str) -> None:
    st.markdown(
        f"""
        <div class="highlight-card">
          <div class="highlight-label">{escape(label)}</div>
          <div class="highlight-value">{escape(value)}</div>
          <div class="highlight-detail">{escape(detail)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def overview_page(frame: pd.DataFrame, source: pd.DataFrame) -> None:
    render_overview_hero(frame, source)
    if frame.empty:
        empty_state()
        return
    render_kpis(frame, source)
    st.markdown("## Cohort overview")
    st.markdown("<p class='section-intro'>A high-level view of patient outcomes, demographics, stage composition, and observed survival duration.</p>", unsafe_allow_html=True)
    st.markdown(f"<div class='filter-summary'><b>Active cohort</b> {escape(filtered_label(frame, source))}</div>", unsafe_allow_html=True)

    first, second = st.columns(2, gap="large")
    with first:
        if "Status" in frame:
            counts = frame["Status"].value_counts(dropna=False).rename_axis("Status").reset_index(name="Patients")
            fig = px.pie(counts, names="Status", values="Patients", hole=.69, color="Status", color_discrete_map=STATUS_COLORS)
            fig.update_traces(textinfo="percent", textposition="inside", hovertemplate="<b>%{label}</b><br>%{value:,} patients<br>%{percent}<extra></extra>")
            fig.add_annotation(text=f"<b>{len(frame):,}</b><br><span style='font-size:10px'>patients</span>", showarrow=False, font={"size": 19, "color": COLORS["navy"]})
            show_chart(fig, "Patient status", "Recorded outcome composition within the active cohort.")
    with second:
        if "Age" in frame:
            fig = px.histogram(frame, x="Age", color="Status" if "Status" in frame else None, nbins=min(20, max(5, frame["Age"].nunique())), barmode="overlay", opacity=.76, color_discrete_map=STATUS_COLORS)
            fig.update_xaxes(title_text="Age (years)")
            fig.update_yaxes(title_text="Patients")
            show_chart(fig, "Patient age distribution", "The distribution of recorded ages, segmented by patient status.")

    first, second = st.columns(2, gap="large")
    with first:
        if "6th Stage" in frame:
            stage_counts = frame["6th Stage"].value_counts().rename_axis("6th Stage").reset_index(name="Patients")
            fig = px.bar(stage_counts, x="6th Stage", y="Patients", text="Patients", color="6th Stage")
            fig.update_traces(texttemplate="%{text:,}", textposition="outside", hovertemplate="<b>%{x}</b><br>%{y:,} patients<extra></extra>")
            fig.update_layout(showlegend=False)
            fig.update_xaxes(title_text="6th stage")
            fig.update_yaxes(title_text="Patients")
            show_chart(fig, "Cancer stage distribution", "Selected patient records grouped by 6th-stage classification.")
    with second:
        if "Survival Months" in frame:
            fig = px.histogram(frame, x="Survival Months", color="Status" if "Status" in frame else None, nbins=22, barmode="overlay", opacity=.74, color_discrete_map=STATUS_COLORS)
            fig.update_xaxes(title_text="Survival months")
            fig.update_yaxes(title_text="Patients")
            show_chart(fig, "Survival months distribution", "Recorded survival durations; this is a descriptive distribution, not a survival probability curve.")

    duplicate_count = int(source.duplicated().sum())
    most_common_age = frame["Age"].mode().iloc[0] if "Age" in frame and frame["Age"].notna().any() else None
    average_tumor = frame["Tumor Size"].mean() if "Tumor Size" in frame else None
    status_counts = frame["Status"].value_counts() if "Status" in frame else pd.Series(dtype="int64")
    alive_rate = status_counts.get("Alive", 0) / len(frame) * 100 if len(frame) else 0
    st.markdown("## Selected-cohort signals")
    signals = st.columns(4, gap="large")
    with signals[0]:
        highlight_card("Most represented age", f"{format_number(most_common_age)} years", "Mode of the active cohort")
    with signals[1]:
        highlight_card("Average tumor size", format_number(average_tumor, 1), "Recorded tumor-size units")
    with signals[2]:
        highlight_card("Observed alive rate", f"{alive_rate:.1f}%", "Based on recorded patient status")
    with signals[3]:
        highlight_card("Source data review", f"{duplicate_count:,} duplicate rows", "Reported without removing source records")


def demographic_page(frame: pd.DataFrame, source: pd.DataFrame) -> None:
    st.markdown("## Demographic analysis")
    st.markdown("<p class='section-intro'>Examine the demographic composition of the active patient cohort and how recorded status varies across groups.</p>", unsafe_allow_html=True)
    if frame.empty:
        empty_state()
        return
    frame = with_age_groups(frame)

    first, second = st.columns((1.15, 1), gap="large")
    with first:
        if "Age" in frame:
            fig = px.histogram(frame, x="Age", color="Status" if "Status" in frame else None, nbins=min(20, max(5, frame["Age"].nunique())), barmode="group", color_discrete_map=STATUS_COLORS)
            fig.update_xaxes(title_text="Age (years)")
            fig.update_yaxes(title_text="Patients")
            show_chart(fig, "Age distribution", "Frequency of patient ages, with recorded patient status available on hover.")
    with second:
        if "Race" in frame:
            counts = frame["Race"].value_counts().rename_axis("Race").reset_index(name="Patients").sort_values("Patients")
            fig = px.bar(counts, y="Race", x="Patients", orientation="h", text="Patients", color="Patients", color_continuous_scale=["#E7E2FC", COLORS["purple"]])
            fig.update_traces(texttemplate="%{text:,}", textposition="outside", hovertemplate="<b>%{y}</b><br>%{x:,} patients<extra></extra>")
            fig.update_layout(coloraxis_showscale=False)
            fig.update_xaxes(title_text="Patients")
            show_chart(fig, "Race distribution", "Representation of recorded race categories in the active cohort.")

    first, second = st.columns((1.1, 1), gap="large")
    with first:
        if "Marital Status" in frame:
            counts = frame["Marital Status"].value_counts().rename_axis("Marital Status").reset_index(name="Patients")
            fig = px.bar(counts, x="Marital Status", y="Patients", text="Patients", color="Patients", color_continuous_scale=["#FFE4EF", COLORS["pink"]])
            fig.update_traces(texttemplate="%{text:,}", textposition="outside", hovertemplate="<b>%{x}</b><br>%{y:,} patients<extra></extra>")
            fig.update_layout(coloraxis_showscale=False)
            fig.update_xaxes(title_text="Marital status", categoryorder="total descending")
            fig.update_yaxes(title_text="Patients")
            show_chart(fig, "Marital status analysis", "Recorded marital-status composition in the active cohort.")
    with second:
        if {"Age Group", "Status"}.issubset(frame.columns):
            age_status = frame.groupby(["Age Group", "Status"], dropna=False).size().reset_index(name="Patients")
            fig = px.bar(age_status, x="Age Group", y="Patients", color="Status", barmode="stack", color_discrete_map=STATUS_COLORS)
            fig.update_xaxes(title_text="Age group")
            fig.update_yaxes(title_text="Patients")
            show_chart(fig, "Patient status by age group", "Recorded patient status across data-derived decade age groups.")


def clinical_page(frame: pd.DataFrame, source: pd.DataFrame) -> None:
    st.markdown("## Clinical analysis")
    st.markdown("<p class='section-intro'>Explore tumor burden, staging, receptor profiles, pathology, and regional lymph-node measures.</p>", unsafe_allow_html=True)
    if frame.empty:
        empty_state()
        return

    first, second = st.columns(2, gap="large")
    with first:
        if "Tumor Size" in frame:
            fig = px.histogram(frame, x="Tumor Size", color="Status" if "Status" in frame else None, nbins=20, barmode="overlay", opacity=.76, color_discrete_map=STATUS_COLORS)
            fig.update_xaxes(title_text="Tumor size")
            fig.update_yaxes(title_text="Patients")
            show_chart(fig, "Tumor size distribution", "Observed spread of recorded tumor-size measurements.")
    with second:
        if "6th Stage" in frame:
            counts = frame["6th Stage"].value_counts().rename_axis("6th Stage").reset_index(name="Patients")
            fig = px.bar(counts, x="6th Stage", y="Patients", text="Patients", color="6th Stage")
            fig.update_traces(texttemplate="%{text:,}", textposition="outside", hovertemplate="<b>%{x}</b><br>%{y:,} patients<extra></extra>")
            fig.update_layout(showlegend=False)
            fig.update_xaxes(title_text="6th stage")
            fig.update_yaxes(title_text="Patients")
            show_chart(fig, "6th stage distribution", "Stage composition in the selected clinical cohort.")

    first, second = st.columns(2, gap="large")
    with first:
        if "T Stage" in frame:
            counts = frame["T Stage"].value_counts().rename_axis("T Stage").reset_index(name="Patients")
            fig = px.bar(counts, y="T Stage", x="Patients", orientation="h", text="Patients", color="Patients", color_continuous_scale=["#E7E2FC", COLORS["purple"]])
            fig.update_traces(texttemplate="%{text:,}", textposition="outside")
            fig.update_layout(coloraxis_showscale=False)
            fig.update_xaxes(title_text="Patients")
            show_chart(fig, "T stage analysis", "Tumor-stage distribution among selected records.")
    with second:
        if "N Stage" in frame:
            counts = frame["N Stage"].value_counts().rename_axis("N Stage").reset_index(name="Patients")
            fig = px.bar(counts, y="N Stage", x="Patients", orientation="h", text="Patients", color="Patients", color_continuous_scale=["#DDF8F3", COLORS["teal"]])
            fig.update_traces(texttemplate="%{text:,}", textposition="outside")
            fig.update_layout(coloraxis_showscale=False)
            fig.update_xaxes(title_text="Patients")
            show_chart(fig, "N stage analysis", "Nodal-stage distribution among selected records.")

    first, second = st.columns(2, gap="large")
    with first:
        receptor_columns = [column for column in ["Estrogen Status", "Progesterone Status"] if column in frame]
        if receptor_columns:
            receptors = frame[receptor_columns].melt(var_name="Receptor", value_name="Result")
            counts = receptors.groupby(["Receptor", "Result"], dropna=False).size().reset_index(name="Patients")
            fig = px.bar(counts, x="Receptor", y="Patients", color="Result", barmode="group", color_discrete_map={"Positive": COLORS["teal"], "Negative": COLORS["pink"]})
            fig.update_xaxes(title_text="Receptor test")
            fig.update_yaxes(title_text="Patients")
            show_chart(fig, "Estrogen and progesterone status", "Recorded receptor test results across the active cohort.")
    with second:
        if {"Grade", "differentiate"}.issubset(frame.columns):
            pathology = frame.groupby(["Grade", "differentiate"], dropna=False).size().reset_index(name="Patients")
            fig = px.bar(pathology, x="Grade", y="Patients", color="differentiate", barmode="stack")
            fig.update_xaxes(title_text="Tumor grade")
            fig.update_yaxes(title_text="Patients")
            show_chart(fig, "Grade and differentiation", "Pathology profile by recorded grade and differentiation category.")

    first, second = st.columns(2, gap="large")
    with first:
        if "Regional Node Examined" in frame:
            fig = px.box(frame, x="Status" if "Status" in frame else None, y="Regional Node Examined", color="Status" if "Status" in frame else None, points="outliers", color_discrete_map=STATUS_COLORS)
            fig.update_layout(showlegend=False)
            fig.update_xaxes(title_text="Recorded patient status")
            fig.update_yaxes(title_text="Regional nodes examined")
            show_chart(fig, "Regional lymph nodes examined", "Distribution of examined regional nodes by recorded patient status.")
    with second:
        if {"Regional Node Examined", "Reginol Node Positive"}.issubset(frame.columns):
            fig = px.scatter(frame, x="Regional Node Examined", y="Reginol Node Positive", color="6th Stage" if "6th Stage" in frame else None, size="Tumor Size" if "Tumor Size" in frame else None, size_max=28, opacity=.72, hover_data=[column for column in ["Age", "Status"] if column in frame])
            fig.update_xaxes(title_text="Regional nodes examined")
            fig.update_yaxes(title_text="Regional nodes positive")
            show_chart(fig, "Regional lymph node relationship", "Positive-node counts compared with the number of regional nodes examined.")

    with st.expander("Open detailed clinical comparisons"):
        first, second = st.columns(2, gap="large")
        with first:
            if {"Tumor Size", "6th Stage"}.issubset(frame.columns):
                fig = px.box(frame, x="6th Stage", y="Tumor Size", color="6th Stage", points="outliers")
                fig.update_layout(showlegend=False)
                fig.update_xaxes(title_text="6th stage")
                fig.update_yaxes(title_text="Tumor size")
                show_chart(fig, "Tumor size by cancer stage", "Tumor-size variation across recorded 6th-stage categories.", height=375)
        with second:
            if {"Estrogen Status", "Status"}.issubset(frame.columns):
                counts = frame.groupby(["Estrogen Status", "Status"], dropna=False).size().reset_index(name="Patients")
                fig = px.bar(counts, x="Estrogen Status", y="Patients", color="Status", barmode="group", color_discrete_map=STATUS_COLORS)
                fig.update_xaxes(title_text="Estrogen receptor status")
                fig.update_yaxes(title_text="Patients")
                show_chart(fig, "Estrogen status by patient outcome", "Recorded patient status by estrogen receptor-status group.", height=375)


def correlation_figure(frame: pd.DataFrame) -> go.Figure | None:
    numeric = frame.select_dtypes(include="number").dropna(axis=1, how="all")
    if numeric.shape[1] < 2:
        return None
    correlation = numeric.corr(numeric_only=True).round(2)
    labels = correlation.columns.tolist()
    hover = [[f"{row}<br>{column}<br>Correlation: {correlation.loc[row, column]:.2f}" for column in labels] for row in labels]
    figure = go.Figure(
        go.Heatmap(
            z=correlation.values,
            x=labels,
            y=labels,
            zmin=-1,
            zmax=1,
            colorscale=[[0, COLORS["pink"]], [.5, "#F7F8FC"], [1, COLORS["teal"]]],
            text=correlation.values,
            texttemplate="%{text:.2f}",
            textfont={"size": 10},
            hovertext=hover,
            hoverinfo="text",
            colorbar={"title": "r", "thickness": 11},
        )
    )
    figure.update_yaxes(autorange="reversed")
    return figure


def survival_page(frame: pd.DataFrame, source: pd.DataFrame) -> None:
    st.markdown("## Survival analysis")
    st.markdown("<p class='section-intro'>Compare recorded survival duration across clinical and demographic groups. These descriptive views are not Kaplan-Meier estimates or survival probabilities.</p>", unsafe_allow_html=True)
    if frame.empty:
        empty_state()
        return
    frame = with_age_groups(frame)

    first, second = st.columns((1.08, 1), gap="large")
    with first:
        if "Survival Months" in frame:
            fig = px.histogram(frame, x="Survival Months", color="Status" if "Status" in frame else None, nbins=22, barmode="overlay", opacity=.75, color_discrete_map=STATUS_COLORS)
            fig.update_xaxes(title_text="Survival months")
            fig.update_yaxes(title_text="Patients")
            show_chart(fig, "Overall survival months", "Distribution of recorded survival duration for selected patient records.")
    with second:
        if {"6th Stage", "Survival Months"}.issubset(frame.columns):
            stage_summary = frame.groupby("6th Stage", dropna=False)["Survival Months"].agg(["mean", "median", "count"]).reset_index()
            fig = px.bar(stage_summary, x="6th Stage", y="mean", color="mean", text="mean", color_continuous_scale=["#E5F6F2", COLORS["teal"]], hover_data={"median": ":.1f", "count": ":,"})
            fig.update_traces(texttemplate="%{text:.1f}", textposition="outside", hovertemplate="<b>%{x}</b><br>Average: %{y:.1f} months<br>Median: %{customdata[0]:.1f} months<br>Patients: %{customdata[1]:,}<extra></extra>")
            fig.update_layout(coloraxis_showscale=False)
            fig.update_xaxes(title_text="6th stage")
            fig.update_yaxes(title_text="Average survival months")
            show_chart(fig, "Average survival by 6th stage", "Average and median recorded survival duration by cancer stage.")

    first, second = st.columns(2, gap="large")
    with first:
        if {"Age Group", "Survival Months"}.issubset(frame.columns):
            fig = px.violin(frame, x="Age Group", y="Survival Months", color="Status" if "Status" in frame else None, box=True, points=False, color_discrete_map=STATUS_COLORS)
            fig.update_xaxes(title_text="Age group")
            fig.update_yaxes(title_text="Survival months")
            show_chart(fig, "Survival comparison by age group", "Distribution of recorded survival months across decade age groups.")
    with second:
        if {"6th Stage", "Status"}.issubset(frame.columns):
            counts = frame.groupby(["6th Stage", "Status"], dropna=False).size().reset_index(name="Patients")
            fig = px.bar(counts, x="6th Stage", y="Patients", color="Status", barmode="stack", color_discrete_map=STATUS_COLORS)
            fig.update_xaxes(title_text="6th stage")
            fig.update_yaxes(title_text="Patients")
            show_chart(fig, "Patient status by cancer stage", "Recorded patient status composition within each cancer stage.")

    first, second = st.columns(2, gap="large")
    with first:
        if {"Estrogen Status", "Survival Months"}.issubset(frame.columns):
            fig = px.box(frame, x="Estrogen Status", y="Survival Months", color="Estrogen Status", points="outliers", color_discrete_map={"Positive": COLORS["teal"], "Negative": COLORS["pink"]})
            fig.update_layout(showlegend=False)
            fig.update_xaxes(title_text="Estrogen receptor status")
            fig.update_yaxes(title_text="Survival months")
            show_chart(fig, "Estrogen status versus survival", "Recorded survival duration grouped by estrogen receptor status.")
    with second:
        if {"Tumor Size", "Survival Months"}.issubset(frame.columns):
            fig = px.scatter(frame, x="Tumor Size", y="Survival Months", color="Status" if "Status" in frame else None, size="Regional Node Examined" if "Regional Node Examined" in frame else None, size_max=30, opacity=.72, color_discrete_map=STATUS_COLORS, hover_data=[column for column in ["Age", "6th Stage", "Estrogen Status"] if column in frame])
            fig.update_xaxes(title_text="Tumor size")
            fig.update_yaxes(title_text="Survival months")
            show_chart(fig, "Tumor size versus survival", "Observed relationship between recorded tumor size and survival duration.")

    with st.expander("Open detailed age and survival comparisons"):
        first, second = st.columns(2, gap="large")
        with first:
            if {"Age", "Tumor Size", "Survival Months"}.issubset(frame.columns):
                fig = px.scatter(frame, x="Age", y="Survival Months", size="Tumor Size", color="Status" if "Status" in frame else None, size_max=31, opacity=.72, color_discrete_map=STATUS_COLORS)
                fig.update_xaxes(title_text="Age (years)")
                fig.update_yaxes(title_text="Survival months")
                show_chart(fig, "Age, tumor size, and survival", "Bubble size represents the recorded tumor size.", height=400)
        with second:
            if {"Age", "Status", "Survival Months"}.issubset(frame.columns):
                fig = px.box(frame, x="Age", y="Survival Months", color="Status", points=False, color_discrete_map=STATUS_COLORS)
                fig.update_xaxes(title_text="Age (years)")
                fig.update_yaxes(title_text="Survival months")
                show_chart(fig, "Survival by individual age and status", "Detailed distribution of recorded survival duration across individual ages.", height=400)

    first, second = st.columns((.9, 1.1), gap="large")
    with first:
        if {"Status", "Survival Months"}.issubset(frame.columns):
            summary = frame.groupby("Status", dropna=False)["Survival Months"].mean().reset_index(name="Average survival months")
            fig = px.bar(summary, x="Average survival months", y="Status", orientation="h", text="Average survival months", color="Status", color_discrete_map=STATUS_COLORS)
            fig.update_traces(texttemplate="%{text:.1f} mo", textposition="outside", hovertemplate="<b>%{y}</b><br>Average survival: %{x:.1f} months<extra></extra>")
            fig.update_layout(showlegend=False)
            fig.update_xaxes(title_text="Average survival months")
            show_chart(fig, "Average survival by patient status", "Mean recorded survival duration by patient-status category.")
    with second:
        correlation = correlation_figure(frame)
        if correlation is not None:
            show_chart(correlation, "Numeric correlation heatmap", "Pairwise correlation among the available numeric variables.", height=400)


def card_html(kind: str, icon_or_number: str, title: str, text: str, important: bool = False) -> str:
    if kind == "insight":
        top = f"<div class='insight-accent'></div><div class='insight-icon'>{escape(icon_or_number)}</div>"
        class_name = "insight-card"
    else:
        top = f"<div class='recommendation-number'>{escape(icon_or_number)}</div>"
        class_name = "recommendation-card important" if important else "recommendation-card"
    return f"<article class='{class_name}'>{top}<h3>{escape(title)}</h3><p>{escape(text)}</p></article>"


def insights_page(frame: pd.DataFrame, source: pd.DataFrame) -> None:
    st.markdown("## Research Insights & Recommendations")
    st.markdown("<p class='section-intro'>Key observations and research directions identified through exploratory data analysis.</p>", unsafe_allow_html=True)

    insights = [
        ("◈", "Demographic Insights", "The dataset provides valuable insights into breast cancer patients' demographic and clinical characteristics."),
        ("◌", "Age Distribution", "Age distribution analysis identifies the most frequently represented patient age groups."),
        ("+", "Patient Status", "Patient status analysis highlights the proportion of patients who are alive or deceased."),
        ("◉", "Tumor Size Analysis", "Tumor size analysis provides insights into variations in tumor measurements across different patient groups."),
        ("↗", "Survival Patterns", "Survival duration analysis examines the recorded survival periods and helps identify potential patterns."),
        ("✦", "Estrogen Status", "Estrogen status analysis reveals differences in patient characteristics based on estrogen receptor status."),
    ]
    for row in (insights[:3], insights[3:]):
        columns = st.columns(3, gap="large")
        for column, (icon, title, text) in zip(columns, row):
            with column:
                st.markdown(card_html("insight", icon, title, text), unsafe_allow_html=True)

    st.markdown("## Research Recommendations")
    st.markdown("<p class='section-intro'>Practical directions for responsible follow-up analysis and interpretation.</p>", unsafe_allow_html=True)
    recommendations = [
        ("1", "Explore age patterns", "Researchers should conduct further studies to understand breast cancer patterns across different age groups.", False),
        ("2", "Add clinical context", "Tumor size should be evaluated in combination with other relevant clinical and demographic factors.", False),
        ("3", "Use robust survival methods", "Survival outcomes should be analyzed using appropriate statistical techniques to ensure reliable interpretations.", True),
        ("4", "Broaden future datasets", "Incorporating recent, diverse, and comprehensive healthcare datasets can enhance the accuracy of future research.", False),
        ("5", "Validate clinically", "All findings should be reviewed and validated by qualified healthcare professionals before being considered for clinical applications.", True),
    ]
    first_row = st.columns(3, gap="large")
    for column, recommendation in zip(first_row, recommendations[:3]):
        with column:
            st.markdown(card_html("recommendation", *recommendation), unsafe_allow_html=True)
    second_row = st.columns(3, gap="large")
    for column, recommendation in zip(second_row[:2], recommendations[3:]):
        with column:
            st.markdown(card_html("recommendation", *recommendation), unsafe_allow_html=True)

    st.info("This application is for exploratory analysis only. Findings describe this dataset and are not clinical guidance.", icon=":material/info:")


def dataset_explorer_page(frame: pd.DataFrame, source: pd.DataFrame) -> None:
    st.markdown("## Dataset explorer")
    st.markdown("<p class='section-intro'>Search, inspect, and export the active cohort without leaving the analytics workspace.</p>", unsafe_allow_html=True)
    if frame.empty:
        empty_state()
        return

    missing_total = int(frame.isna().sum().sum())
    metrics = st.columns(4, gap="large")
    explorer_stats = [
        ("Active rows", format_number(len(frame))),
        ("Available fields", format_number(len(frame.columns))),
        ("Missing values", format_number(missing_total)),
        ("Duplicate source rows", format_number(int(source.duplicated().sum()))),
    ]
    for column, (label, value) in zip(metrics, explorer_stats):
        with column:
            st.markdown(f"<div class='explorer-stat'><span>{escape(label)}</span><strong>{escape(value)}</strong></div>", unsafe_allow_html=True)

    selected_columns = st.multiselect("Columns to display", list(frame.columns), default=list(frame.columns), key="explorer_columns")
    query = st.text_input("Search active cohort", placeholder="Search any displayed field…", key="explorer_search")
    displayed_columns = selected_columns or list(frame.columns)
    explored = frame.copy()
    if query.strip():
        query_text = query.strip()
        matches = explored[displayed_columns].astype("string").apply(lambda series: series.str.contains(query_text, case=False, regex=False, na=False))
        explored = explored[matches.any(axis=1)]

    st.caption(f"Showing {len(explored):,} matching records across {len(displayed_columns)} selected fields.")
    st.dataframe(explored[displayed_columns], width="stretch", height=445, hide_index=True)
    st.download_button(
        "Download explorer results as CSV",
        data=explored[displayed_columns].to_csv(index=False).encode("utf-8"),
        file_name="carelens_explorer_results.csv",
        mime="text/csv",
    )

    first, second = st.columns((1.05, .95), gap="large")
    with first:
        st.markdown("### Missing value overview")
        missing = frame.isna().sum().rename_axis("Field").reset_index(name="Missing values")
        missing["Missing rate"] = (missing["Missing values"] / len(frame) * 100).round(2)
        st.dataframe(missing.sort_values(["Missing values", "Field"], ascending=[False, True]), width="stretch", hide_index=True)
    with second:
        st.markdown("### Field types & summaries")
        summaries = pd.DataFrame({
            "Field": frame.columns,
            "Data type": [str(dtype) for dtype in frame.dtypes],
            "Unique values": [frame[column].nunique(dropna=True) for column in frame.columns],
        })
        st.dataframe(summaries, width="stretch", hide_index=True)


def render_footer() -> None:
    st.markdown("<div class='footer'>CareLens Analytics &nbsp;|&nbsp; Exploratory Data Analysis</div>", unsafe_allow_html=True)


def main() -> None:
    inject_styles()
    if not DATA_PATH.exists():
        st.error("The source dataset 'Breast_Cancer.csv' was not found next to app.py.")
        st.stop()
    try:
        source = load_data(str(DATA_PATH))
    except Exception as exc:
        st.error(f"The source dataset could not be loaded: {exc}")
        st.stop()

    page, filtered = sidebar_and_filters(source)
    render_header(page, filtered, source)
    if page == "Overview":
        overview_page(filtered, source)
    elif page == "Demographic Analysis":
        demographic_page(filtered, source)
    elif page == "Clinical Analysis":
        clinical_page(filtered, source)
    elif page == "Survival Analysis":
        survival_page(filtered, source)
    elif page == "Insights & Recommendations":
        insights_page(filtered, source)
    else:
        dataset_explorer_page(filtered, source)
    render_footer()


if __name__ == "__main__":
    main()
