import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime
import json
import os

st.set_page_config(
    page_title="Sellers.json Analyzer",
    page_icon="📊",
    layout="wide"
)

# ─── Ogury Brand Colors (Light Theme) ────────────────────────────────────────
OGURY = {
    "dark_teal":  "#005959",
    "turquoise":  "#0A9999",
    "lime":       "#C3EA76",
    "cream":      "#FFF9EC",
    "ocean":      "#003B63",
    "white":      "#FFFFFF",
    # Light theme extras
    "teal_light": "#E6F4F4",   # very light teal for sidebar bg
    "teal_mid":   "#D0EBEB",   # for hover/card borders
    "lime_light": "#F0FAE0",   # light lime for accents
    "text_dark":  "#1A1A2E",   # near-black for readability
    "text_mid":   "#4A4A6A",   # body text
}

st.markdown(f"""
<style>
    /* ── Global ── */
    html, body, [class*="css"] {{
        font-family: 'Montserrat', 'Inter', sans-serif;
        color: {OGURY['text_dark']};
    }}
    .stApp {{
        background-color: {OGURY['white']};
    }}

    /* ── Top header bar ── */
    header[data-testid="stHeader"] {{
        background: {OGURY['white']};
        border-bottom: 2px solid {OGURY['teal_mid']};
    }}

    /* ── Sidebar — light teal tint ── */
    section[data-testid="stSidebar"] {{
        background: {OGURY['teal_light']} !important;
        border-right: 2px solid {OGURY['teal_mid']};
    }}
    section[data-testid="stSidebar"] * {{
        color: {OGURY['text_dark']} !important;
    }}
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: {OGURY['dark_teal']} !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiselect label,
    section[data-testid="stSidebar"] .stTextInput label {{
        color: {OGURY['dark_teal']} !important;
        font-weight: 600 !important;
    }}
    section[data-testid="stSidebar"] .stButton > button {{
        background: {OGURY['dark_teal']};
        color: {OGURY['lime']};
        border: none;
        border-radius: 20px;
        font-weight: 700;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background: {OGURY['turquoise']};
        color: white;
    }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {{
        background: {OGURY['teal_light']};
        border-radius: 10px 10px 0 0;
        gap: 2px;
        padding: 6px 6px 0 6px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: white;
        border-radius: 8px 8px 0 0;
        border: 1px solid {OGURY['teal_mid']};
        border-bottom: none;
        color: {OGURY['dark_teal']};
        font-weight: 600;
        padding: 8px 20px;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        background: {OGURY['lime_light']};
        color: {OGURY['dark_teal']};
    }}
    .stTabs [aria-selected="true"] {{
        background: {OGURY['dark_teal']} !important;
        color: {OGURY['lime']} !important;
        border-color: {OGURY['dark_teal']} !important;
    }}
    .stTabs [data-baseweb="tab-panel"] {{
        background: white;
        border-radius: 0 8px 8px 8px;
        border: 1px solid {OGURY['teal_mid']};
        padding: 1.5rem;
    }}

    /* ── Metric cards ── */
    .metric-card {{
        background: {OGURY['white']};
        border-radius: 12px;
        padding: 1rem 1.2rem;
        border: 1px solid {OGURY['teal_mid']};
        border-left: 4px solid {OGURY['turquoise']};
        box-shadow: 0 1px 6px rgba(0,89,89,0.06);
        transition: all 0.2s ease;
    }}
    .metric-card:hover {{
        box-shadow: 0 4px 14px rgba(0,89,89,0.12);
        border-left-color: {OGURY['dark_teal']};
        background: {OGURY['teal_light']};
    }}
    .metric-card .metric-label {{
        font-size: 11px;
        color: {OGURY['turquoise']};
        margin-bottom: 6px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }}
    .metric-card .metric-value {{
        font-size: 30px;
        font-weight: 800;
        color: {OGURY['dark_teal']};
        line-height: 1.2;
    }}

    /* ── Compare cards ── */
    .compare-header {{
        background: {OGURY['teal_light']};
        color: {OGURY['dark_teal']};
        border: 1px solid {OGURY['teal_mid']};
        border-bottom: 2px solid {OGURY['turquoise']};
        border-radius: 10px 10px 0 0;
        padding: 10px 16px;
        font-weight: 700;
        font-size: 15px;
    }}
    .compare-body {{
        background: white;
        border: 1px solid {OGURY['teal_mid']};
        border-top: none;
        border-radius: 0 0 10px 10px;
        padding: 1rem;
    }}

    /* ── Tables ── */
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 0.5rem; }}
    thead tr {{ background: {OGURY['teal_light']}; border-bottom: 2px solid {OGURY['turquoise']}; }}
    thead th {{ padding: 10px 14px; text-align: left; font-weight: 700;
                color: {OGURY['dark_teal']}; font-size: 13px; }}
    tbody tr {{ border-bottom: 1px solid #f0f0f0; }}
    tbody tr:hover {{ background: {OGURY['lime_light']}; }}
    tbody td {{ padding: 8px 14px; color: {OGURY['text_dark']}; vertical-align: middle; }}

    /* ── Page title ── */
    .app-title {{
        background: {OGURY['teal_light']};
        border: 1px solid {OGURY['teal_mid']};
        border-left: 5px solid {OGURY['dark_teal']};
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .app-title h1 {{
        margin: 0;
        font-size: 1.6rem;
        font-weight: 800;
        color: {OGURY['dark_teal']};
    }}
    .app-title span {{
        font-size: 13px;
        color: {OGURY['turquoise']};
        margin-top: 2px;
    }}

    /* ── Section headers ── */
    .section-header {{
        color: {OGURY['dark_teal']};
        font-weight: 700;
        font-size: 1.1rem;
        border-left: 4px solid {OGURY['lime']};
        padding-left: 10px;
        margin: 1rem 0 0.6rem 0;
    }}

    /* ── Rating box ── */
    .rating-box {{
        background: white;
        border: 1px solid {OGURY['teal_mid']};
        border-left: 4px solid {OGURY['turquoise']};
        border-radius: 12px;
        padding: 14px 16px;
        margin-top: 8px;
    }}

    /* ── Diff badges ── */
    .diff-pos {{ color: #16a34a; font-weight: 700; }}
    .diff-neg {{ color: #dc2626; font-weight: 700; }}
    .diff-neu {{ color: #6b7280; font-weight: 600; }}

    /* ── Buttons ── */
    .stButton > button {{
        border-radius: 20px;
        border: 2px solid {OGURY['turquoise']};
        color: {OGURY['dark_teal']};
        font-weight: 600;
    }}
    .stDownloadButton > button {{
        background: {OGURY['dark_teal']};
        color: {OGURY['lime']};
        border-radius: 20px;
        border: none;
        font-weight: 700;
    }}
</style>
""", unsafe_allow_html=True)

# ─── Brand Colors for charts ──────────────────────────────────────────────────
TYPE_COLORS = {
    "BOTH":         "#0A9999",
    "PUBLISHER":    "#005959",
    "INTERMEDIARY": "#C3EA76",
    "UNKNOWN":      "#888780",
}
CHART_SCALE = ["#C3EA76", "#0A9999", "#005959"]

SOURCES = {
    "Ogury":    "https://sellers.ogury.com/",
    "Pubmatic": "https://cdn.pubmatic.com/sellers/data/sellers.json",
    "Teads":    "https://sellers.teads.tv/sellers.json",
}

# ─── Persistent ratings via st.session_state + storage API ───────────────────
RATINGS_FILE = "ratings.json"

def save_rating(score: int):
    data = {"ratings": []}
    if os.path.exists(RATINGS_FILE):
        try:
            with open(RATINGS_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            data = {"ratings": []}
    data["ratings"].append(score)
    with open(RATINGS_FILE, "w") as f:
        json.dump(data, f)

def get_ratings():
    if not os.path.exists(RATINGS_FILE):
        return None, 0
    try:
        with open(RATINGS_FILE, "r") as f:
            data = json.load(f)
    except Exception:
        return None, 0
    ratings = data.get("ratings", [])
    if not ratings:
        return None, 0
    return round(sum(ratings) / len(ratings), 2), len(ratings)

# ─── Data loading ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data(url: str):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; SellersJsonAnalyzer/1.0)"}
    resp = requests.get(url, timeout=15, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    sellers = data.get("sellers", [])
    df = pd.DataFrame(sellers)
    df["seller_type"] = df["seller_type"].fillna("UNKNOWN")
    df["name"]        = df["name"].fillna("N/A")
    df["domain"]      = df["domain"].fillna("N/A")
    return df, data.get("version"), data.get("identifiers", [])

# ─── Title bar ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-title">
    <div>
        <h1>📊 Sellers.json Analyzer</h1>
        <span>Powered by Ogury Supply Intelligence</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 📡 Data Source")
    selected_source = st.selectbox(
        "Primary source",
        options=list(SOURCES.keys()),
        help="Select the adtech platform to analyze"
    )

    st.markdown(f"### 🆚 Compare Mode")
    enable_compare = st.toggle("Enable comparison", value=False)
    compare_source = None
    if enable_compare:
        other_opts = [s for s in SOURCES.keys() if s != selected_source]
        compare_source = st.selectbox("Compare with", options=other_opts)

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("### 📊 Display Options")
    top_n_domains = st.selectbox("Top domains to display", [5, 10, 20, 30, 50], index=1)

    st.markdown("### 💬 Feedback")
    GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSe0Go2SeI3R_ceb9ekeX285dKvfHip9pM_KAtDngjNkiis1eQ/viewform?usp=pp_url"
    st.markdown(f'<a href="{GOOGLE_FORM_URL}" target="_blank" style="display:inline-block;background:{OGURY["dark_teal"]};color:{OGURY["lime"]};border-radius:20px;padding:8px 18px;font-weight:700;text-decoration:none;font-size:13px;">📝 Open Feedback Form</a>', unsafe_allow_html=True)

    # ── Star rating — persists via file, survives reruns ──
    st.markdown("<br>", unsafe_allow_html=True)
    if "submitted_rating" not in st.session_state:
        st.session_state.submitted_rating = False

    if not st.session_state.submitted_rating:
        st.markdown(f'<div style="color:{OGURY["dark_teal"]};font-weight:700;margin-bottom:4px;">⭐ Rate this app</div>', unsafe_allow_html=True)
        selected = st.feedback("stars", key="user_rating")
        if selected is not None:
            save_rating(selected + 1)
            st.session_state.submitted_rating = True
            st.rerun()
    else:
        st.markdown(f'<div style="color:{OGURY["dark_teal"]};font-weight:600;">✅ Thanks for rating!</div>', unsafe_allow_html=True)

    avg_rating, num_responses = get_ratings()
    if avg_rating is not None:
        pct = int((avg_rating - 1) / 4 * 100)
        filled = round(avg_rating)
        stars = "".join(["★" if i <= filled else "☆" for i in range(1, 6)])
        st.markdown(f"""
        <div class="rating-box">
            <div style="font-size:10px;color:{OGURY["turquoise"]};font-weight:700;text-transform:uppercase;
                        letter-spacing:0.8px;margin-bottom:4px;">⭐ User Satisfaction</div>
            <div style="font-size:1.9rem;font-weight:800;color:{OGURY['lime']};line-height:1;margin-bottom:2px;">
                {avg_rating}&nbsp;<span style="font-size:12px;font-weight:400;color:#a0d4d4;">/ 5  ({num_responses} votes)</span>
            </div>
            <div style="font-size:20px;color:#f59e0b;margin-bottom:8px;letter-spacing:2px;">{stars}</div>
            <div style="background:rgba(255,255,255,0.15);border-radius:999px;height:8px;overflow:hidden;">
                <div style="background:{OGURY['lime']};height:8px;width:{pct}%;border-radius:999px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="color:{OGURY["turquoise"]};font-size:12px;">No ratings yet — be the first!</div>', unsafe_allow_html=True)

    st.markdown(f'<div style="color:{OGURY["text_mid"]};font-size:11px;margin-top:16px;">📌 Admin: joaquim.francalanci@ogury.co</div>', unsafe_allow_html=True)

# ─── Load primary data ────────────────────────────────────────────────────────
active_url = SOURCES[selected_source]
st.caption(f"**Active Source:** `{active_url}`")

with st.spinner(f"Loading {selected_source} sellers.json..."):
    try:
        df, version, identifiers = load_data(active_url)
    except Exception as e:
        st.error(f"Failed to load {selected_source}: {e}")
        st.stop()

if df.empty:
    st.warning("No sellers found in this file.")
    st.stop()

# ─── Load compare data ────────────────────────────────────────────────────────
df_cmp, version_cmp, identifiers_cmp = None, None, None
if enable_compare and compare_source:
    cmp_url = SOURCES[compare_source]
    with st.spinner(f"Loading {compare_source} for comparison..."):
        try:
            df_cmp, version_cmp, identifiers_cmp = load_data(cmp_url)
        except Exception as e:
            st.warning(f"Could not load {compare_source}: {e}")
            df_cmp = None

# ─── KPI Metrics ─────────────────────────────────────────────────────────────
def render_metrics(dataframe, label=""):
    publishers    = len(dataframe[dataframe["seller_type"] == "PUBLISHER"])
    intermediaries = len(dataframe[dataframe["seller_type"] == "INTERMEDIARY"])
    both          = len(dataframe[dataframe["seller_type"] == "BOTH"])
    cols = st.columns(4)
    for col, title, val in zip(cols,
        ["Total Sellers", "Publishers", "Intermediaries", "Both"],
        [len(dataframe), publishers, intermediaries, both]):
        col.markdown(f'<div class="metric-card"><div class="metric-label">{label}{title}</div><div class="metric-value">{val:,}</div></div>', unsafe_allow_html=True)

render_metrics(df)

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tabs = ["📈 Overview", "🔍 Search & Filter", "🌐 Domain Analysis", "📋 Raw Data"]
if enable_compare and df_cmp is not None:
    tabs.append("🆚 Compare")

tab_objects = st.tabs(tabs)
tab1, tab2, tab3, tab4 = tab_objects[:4]
tab_compare = tab_objects[4] if len(tab_objects) == 5 else None

# ── Tab 1: Overview ───────────────────────────────────────────────────────────
with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        type_counts = df["seller_type"].value_counts().reset_index()
        type_counts.columns = ["Seller Type", "Count"]
        fig_pie = px.pie(type_counts, names="Seller Type", values="Count",
                         title="Seller Type Distribution", color="Seller Type",
                         color_discrete_map=TYPE_COLORS, hole=0.4)
        fig_pie.update_traces(textposition="outside", textinfo="percent+label")
        fig_pie.update_layout(showlegend=False, height=380,
                               paper_bgcolor="white", plot_bgcolor="white")
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_b:
        fig_bar = px.bar(type_counts, x="Seller Type", y="Count",
                         title="Seller Count by Type", color="Seller Type",
                         color_discrete_map=TYPE_COLORS, text="Count")
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(showlegend=False, height=380, yaxis_title="Count",
                               paper_bgcolor="white", plot_bgcolor="white")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown(f'<div class="section-header">Top {top_n_domains} Domains by Seller Count</div>', unsafe_allow_html=True)
    domain_counts = df[df["domain"] != "N/A"]["domain"].value_counts().head(top_n_domains).reset_index()
    domain_counts.columns = ["Domain", "Count"]
    fig_domains = px.bar(domain_counts, x="Count", y="Domain", orientation="h",
                         color="Count", color_continuous_scale=CHART_SCALE,
                         title=f"Top {top_n_domains} Domains")
    fig_domains.update_layout(height=550, yaxis={"categoryorder": "total ascending"},
                               coloraxis_showscale=False, paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(fig_domains, use_container_width=True)

# ── Tab 2: Search & Filter ────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">Search & Filter Sellers</div>', unsafe_allow_html=True)
    col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
    with col_f1:
        search_query = st.text_input("🔍 Search by name, domain or seller ID",
                                     placeholder="e.g. Google, publisher.com...")
    with col_f2:
        type_filter = st.multiselect("Seller Type",
                                     options=sorted(df["seller_type"].unique()),
                                     default=sorted(df["seller_type"].unique()))
    with col_f3:
        sort_by = st.selectbox("Sort by", ["name", "domain", "seller_type", "seller_id"])

    filtered = df[df["seller_type"].isin(type_filter)].copy()
    if search_query:
        mask = (
            filtered["name"].str.contains(search_query, case=False, na=False) |
            filtered["domain"].str.contains(search_query, case=False, na=False) |
            filtered["seller_id"].str.contains(search_query, case=False, na=False)
        )
        filtered = filtered[mask]
    filtered = filtered.sort_values(sort_by)
    st.markdown(f"**{len(filtered):,}** results")

    def tag_html(t):
        css = {
            "BOTH":         f"background:#d4f5e2;color:{OGURY['dark_teal']}",
            "PUBLISHER":    f"background:#cff4fc;color:{OGURY['ocean']}",
            "INTERMEDIARY": f"background:#e8f8ee;color:{OGURY['dark_teal']}",
        }.get(t, "background:#f0f0f0;color:#666")
        return f'<span style="display:inline-block;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:600;{css}">{t}</span>'

    display_df = filtered[["name", "domain", "seller_type", "seller_id"]].copy().reset_index(drop=True)
    display_df["seller_type"] = display_df["seller_type"].apply(tag_html)
    st.write(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download filtered results as CSV", csv,
                       f"{selected_source.lower()}_sellers_filtered.csv", "text/csv")

# ── Tab 3: Domain Analysis ────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">Domain Analysis</div>', unsafe_allow_html=True)
    col_d_opt1, col_d_opt2 = st.columns(2)
    with col_d_opt1:
        top_tlds_to_show = st.selectbox("Number of TLDs to display", [10, 15, 20, 25], index=1)
    with col_d_opt2:
        show_multi_domain_threshold = st.number_input("Minimum seller IDs per domain",
                                                      min_value=1, max_value=10, value=2, step=1)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown("**Top Level Domain (TLD) Distribution**")
        tld_series = df[df["domain"] != "N/A"]["domain"].dropna().str.extract(r'\.([a-zA-Z]{2,6})$')[0]
        tld_counts = tld_series.value_counts().head(top_tlds_to_show).reset_index()
        tld_counts.columns = ["TLD", "Count"]
        fig_tld = px.bar(tld_counts, x="TLD", y="Count", color="Count",
                         color_continuous_scale=CHART_SCALE, title=f"Top {top_tlds_to_show} TLDs")
        fig_tld.update_layout(coloraxis_showscale=False, height=380,
                               paper_bgcolor="white", plot_bgcolor="white")
        st.plotly_chart(fig_tld, use_container_width=True)
    with col_d2:
        st.markdown("**Seller Type by TLD (Top 10)**")
        df_tld = df[df["domain"] != "N/A"].copy()
        df_tld["tld"] = df_tld["domain"].str.extract(r'\.([a-zA-Z]{2,6})$')[0]
        top_tlds = df_tld["tld"].value_counts().head(10).index
        tld_type = df_tld[df_tld["tld"].isin(top_tlds)].groupby(["tld", "seller_type"]).size().reset_index(name="count")
        fig_tld_type = px.bar(tld_type, x="tld", y="count", color="seller_type",
                              color_discrete_map=TYPE_COLORS, title="Seller Type by TLD", barmode="stack")
        fig_tld_type.update_layout(height=380, xaxis_title="TLD", yaxis_title="Count",
                                    paper_bgcolor="white", plot_bgcolor="white")
        st.plotly_chart(fig_tld_type, use_container_width=True)

    st.markdown(f'<div class="section-header">Domains with {show_multi_domain_threshold}+ Seller IDs</div>', unsafe_allow_html=True)
    multi_domain = df[df["domain"] != "N/A"].groupby("domain").agg(
        seller_count=("seller_id", "count"),
        seller_types=("seller_type", lambda x: ", ".join(sorted(x.unique())))
    ).reset_index().sort_values("seller_count", ascending=False)
    multi_domain = multi_domain[multi_domain["seller_count"] >= show_multi_domain_threshold]
    st.markdown(f"**{len(multi_domain):,}** domains with {show_multi_domain_threshold}+ seller IDs")
    st.dataframe(multi_domain.head(50).reset_index(drop=True), use_container_width=True, height=350,
                 column_config={
                     "domain":       st.column_config.TextColumn("Domain", width="medium"),
                     "seller_count": st.column_config.NumberColumn("# Seller IDs", width="small"),
                     "seller_types": st.column_config.TextColumn("Types", width="medium"),
                 })

# ── Tab 4: Raw Data ───────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-header">Raw Data</div>', unsafe_allow_html=True)
    st.markdown(f"**Version:** {version} | **Identifiers:** {identifiers}")
    st.dataframe(df.reset_index(drop=True), use_container_width=True, height=600)
    csv_all = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download full sellers.json as CSV", csv_all,
                       f"{selected_source.lower()}_sellers_full.csv", "text/csv")

# ── Tab 5: Compare ────────────────────────────────────────────────────────────
if tab_compare is not None and df_cmp is not None:
    with tab_compare:
        st.markdown(f'<div class="section-header">🆚 {selected_source} vs {compare_source}</div>', unsafe_allow_html=True)

        # ── KPI comparison ──
        def kpi(df_):
            pub  = len(df_[df_["seller_type"] == "PUBLISHER"])
            inter = len(df_[df_["seller_type"] == "INTERMEDIARY"])
            both  = len(df_[df_["seller_type"] == "BOTH"])
            domains = df_[df_["domain"] != "N/A"]["domain"].nunique()
            return {"Total Sellers": len(df_), "Publishers": pub,
                    "Intermediaries": inter, "Both": both, "Unique Domains": domains}

        kpi_a = kpi(df)
        kpi_b = kpi(df_cmp)

        def diff_badge(a, b):
            d = a - b
            if d > 0:   return f'<span class="diff-pos">▲ {d:+,}</span>'
            elif d < 0: return f'<span class="diff-neg">▼ {d:,}</span>'
            else:        return f'<span class="diff-neu">= same</span>'

        # Side-by-side metric cards
        col_left, col_sep, col_right = st.columns([5, 1, 5])
        with col_left:
            st.markdown(f'<div class="compare-header">📦 {selected_source}</div><div class="compare-body">', unsafe_allow_html=True)
            render_metrics(df)
            st.markdown('</div>', unsafe_allow_html=True)
        with col_sep:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            st.markdown(f'<div style="text-align:center;font-size:2rem;color:{OGURY["dark_teal"]};font-weight:800;">VS</div>', unsafe_allow_html=True)
        with col_right:
            st.markdown(f'<div class="compare-header">📦 {compare_source}</div><div class="compare-body">', unsafe_allow_html=True)
            render_metrics(df_cmp)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Delta table ──
        st.markdown('<div class="section-header">Delta Summary</div>', unsafe_allow_html=True)
        delta_rows = []
        for key in kpi_a:
            a, b = kpi_a[key], kpi_b[key]
            pct = round((a - b) / b * 100, 1) if b else 0
            delta_rows.append({
                "Metric": key,
                selected_source: f"{a:,}",
                compare_source: f"{b:,}",
                "Difference": a - b,
                "% Δ": f"{pct:+.1f}%"
            })
        delta_df = pd.DataFrame(delta_rows)
        st.dataframe(delta_df, use_container_width=True, hide_index=True,
                     column_config={
                         "Difference": st.column_config.NumberColumn("Difference", format="%+d"),
                     })

        # ── Seller type comparison chart ──
        st.markdown('<div class="section-header">Seller Type Distribution — Side by Side</div>', unsafe_allow_html=True)
        tc_a = df["seller_type"].value_counts().rename(selected_source)
        tc_b = df_cmp["seller_type"].value_counts().rename(compare_source)
        tc_merged = pd.concat([tc_a, tc_b], axis=1).fillna(0).reset_index()
        tc_merged.columns = ["Seller Type", selected_source, compare_source]
        tc_melted = tc_merged.melt(id_vars="Seller Type", var_name="Source", value_name="Count")

        source_colors = {selected_source: OGURY["dark_teal"], compare_source: OGURY["turquoise"]}
        fig_cmp = px.bar(tc_melted, x="Seller Type", y="Count", color="Source",
                         barmode="group", color_discrete_map=source_colors,
                         title="Seller Type: Side-by-Side Comparison", text="Count")
        fig_cmp.update_traces(textposition="outside")
        fig_cmp.update_layout(height=420, paper_bgcolor="white", plot_bgcolor="white")
        st.plotly_chart(fig_cmp, use_container_width=True)

        # ── Top domains comparison ──
        st.markdown('<div class="section-header">Top 15 Domains — Overlap Analysis</div>', unsafe_allow_html=True)
        top_a = set(df[df["domain"] != "N/A"]["domain"].value_counts().head(50).index)
        top_b = set(df_cmp[df_cmp["domain"] != "N/A"]["domain"].value_counts().head(50).index)
        shared = top_a & top_b
        only_a = top_a - top_b
        only_b = top_b - top_a

        col_ov1, col_ov2, col_ov3 = st.columns(3)
        col_ov1.markdown(f'<div class="metric-card"><div class="metric-label">Shared Top Domains</div><div class="metric-value" style="color:{OGURY["turquoise"]}">{len(shared)}</div></div>', unsafe_allow_html=True)
        col_ov2.markdown(f'<div class="metric-card"><div class="metric-label">Only in {selected_source}</div><div class="metric-value" style="color:{OGURY["dark_teal"]}">{len(only_a)}</div></div>', unsafe_allow_html=True)
        col_ov3.markdown(f'<div class="metric-card"><div class="metric-label">Only in {compare_source}</div><div class="metric-value" style="color:{OGURY["dark_teal"]}">{len(only_b)}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_sh1, col_sh2, col_sh3 = st.columns(3)
        with col_sh1:
            st.markdown(f"**🤝 Shared domains (top 50)**")
            st.write(sorted(shared)[:20] if shared else ["None"])
        with col_sh2:
            st.markdown(f"**Only in {selected_source}**")
            st.write(sorted(only_a)[:15] if only_a else ["None"])
        with col_sh3:
            st.markdown(f"**Only in {compare_source}**")
            st.write(sorted(only_b)[:15] if only_b else ["None"])

        # ── Seller ID overlap ──
        st.markdown('<div class="section-header">Seller ID Overlap</div>', unsafe_allow_html=True)
        ids_a = set(df["seller_id"].dropna())
        ids_b = set(df_cmp["seller_id"].dropna())
        shared_ids = ids_a & ids_b
        col_id1, col_id2, col_id3 = st.columns(3)
        col_id1.markdown(f'<div class="metric-card"><div class="metric-label">Shared Seller IDs</div><div class="metric-value" style="color:{OGURY["turquoise"]}">{len(shared_ids):,}</div></div>', unsafe_allow_html=True)
        col_id2.markdown(f'<div class="metric-card"><div class="metric-label">Only in {selected_source}</div><div class="metric-value">{len(ids_a - ids_b):,}</div></div>', unsafe_allow_html=True)
        col_id3.markdown(f'<div class="metric-card"><div class="metric-label">Only in {compare_source}</div><div class="metric-value">{len(ids_b - ids_a):,}</div></div>', unsafe_allow_html=True)

        if shared_ids:
            if st.checkbox("Show shared seller IDs details"):
                shared_detail = df[df["seller_id"].isin(shared_ids)][["seller_id", "name", "domain", "seller_type"]].copy()
                shared_detail = shared_detail.rename(columns={
                    "name": f"name ({selected_source})",
                    "domain": f"domain ({selected_source})",
                    "seller_type": f"type ({selected_source})"
                })
                cmp_detail = df_cmp[df_cmp["seller_id"].isin(shared_ids)][["seller_id", "seller_type"]].rename(
                    columns={"seller_type": f"type ({compare_source})"}
                )
                merged_detail = shared_detail.merge(cmp_detail, on="seller_id", how="left")
                st.dataframe(merged_detail.reset_index(drop=True), use_container_width=True, height=350)

        # ── Download compare summary ──
        compare_csv = delta_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            f"⬇️ Download comparison summary CSV",
            compare_csv,
            f"compare_{selected_source}_vs_{compare_source}.csv",
            "text/csv"
        )

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:2rem;padding:12px 20px;background:{OGURY['teal_light']};
            border:1px solid {OGURY['teal_mid']};border-left:4px solid {OGURY['dark_teal']};
            border-radius:10px;color:{OGURY['text_mid']};font-size:12px;text-align:center;">
    Data loaded live · Cached for 1 hour · Built with Streamlit & Ogury brand ·
    <span style="color:{OGURY['lime']}">💡 Tip: Enable Compare Mode in the sidebar to benchmark two sources</span>
</div>
""", unsafe_allow_html=True)