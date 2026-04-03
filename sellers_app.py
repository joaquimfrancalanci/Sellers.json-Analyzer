import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
from urllib.parse import urlparse

st.set_page_config(
    page_title="Sellers.json Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp { background: #0d0d0d; color: #f0f0f0; }

section[data-testid="stSidebar"] {
    background: #111111;
    border-right: 1px solid #1e1e1e;
}

.brand-tag {
    display: inline-block;
    background: #1D9E75;
    color: #fff !important;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    padding: 3px 10px;
    border-radius: 3px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.page-title {
    font-size: 2rem;
    font-weight: 600;
    color: #f5f5f5;
    line-height: 1.2;
    margin: 4px 0 6px 0;
}

.page-subtitle { color: #555; font-size: 0.9rem; margin: 0; }

.section-title {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #333;
    font-family: 'DM Mono', monospace;
    margin: 1.2rem 0 0.6rem 0;
    padding-bottom: 6px;
    border-bottom: 1px solid #1a1a1a;
}

div[data-testid="stMetric"] {
    background: #131313 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 10px !important;
    padding: 1rem 1.2rem !important;
}
div[data-testid="stMetric"] label {
    color: #444 !important;
    font-size: 10px !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-family: 'DM Mono', monospace;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #f0f0f0 !important;
    font-size: 1.7rem !important;
    font-weight: 600 !important;
}
div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    font-size: 11px !important;
    font-family: 'DM Mono', monospace !important;
}

.stTextInput > div > div > input {
    background: #131313 !important;
    border: 1px solid #222 !important;
    border-radius: 8px !important;
    color: #e0e0e0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 12px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #1D9E75 !important;
    box-shadow: 0 0 0 1px #1D9E75 !important;
}

.stSelectbox > div > div, .stMultiSelect > div > div {
    background: #131313 !important;
    border: 1px solid #222 !important;
    border-radius: 8px !important;
    color: #e0e0e0 !important;
}

.stButton > button {
    background: #131313 !important;
    color: #888 !important;
    border: 1px solid #222 !important;
    border-radius: 7px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    border-color: #1D9E75 !important;
    color: #1D9E75 !important;
}
.stButton > button[kind="primary"] {
    background: #1D9E75 !important;
    color: white !important;
    border: none !important;
}

.stDownloadButton > button {
    background: transparent !important;
    border: 1px solid #222 !important;
    color: #666 !important;
    border-radius: 7px !important;
    font-size: 12px !important;
}
.stDownloadButton > button:hover {
    border-color: #1D9E75 !important;
    color: #1D9E75 !important;
}

.stTabs [data-baseweb="tab-list"] {
    border-bottom: 1px solid #1a1a1a !important;
    background: transparent !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #444 !important;
    padding: 0.5rem 1.2rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #1D9E75 !important;
    border-bottom: 2px solid #1D9E75 !important;
}

.source-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #0d0d0d;
    border: 1px solid #1e1e1e;
    border-radius: 20px;
    padding: 4px 10px;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #444;
    margin-top: 10px;
}
.green-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: #1D9E75;
    display: inline-block;
}

.stat-row {
    color: #555;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    margin: 4px 0;
}

.err {
    background: #150d0d;
    border: 1px solid #3a1a1a;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    color: #E24B4A;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

OGURY_URL = "https://sellers.ogury.com/"
QUICK_URLS = [
    ("Ogury", "https://sellers.ogury.com/"),
    ("Pubmatic", "https://cdn.pubmatic.com/sellers/data/sellers.json"),
    ("Teads", "https://sellers.teads.tv/sellers.json"),
    ("Xandr", "https://xandr.com/sellers.json"),
    ("Magnite", "https://www.magnite.com/sellers.json"),
    ("The Trade Desk", "https://thetradedesk.com/sellers.json"),
]

@st.cache_data(ttl=3600, show_spinner=False)
def load_sellers(url: str):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; SellersJsonAnalyzer/1.0)"}
    resp = requests.get(url, timeout=20, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    sellers = data.get("sellers", [])
    df = pd.DataFrame(sellers) if sellers else pd.DataFrame()
    if not df.empty:
        df["seller_type"] = df.get("seller_type", pd.Series(dtype=str)).fillna("UNKNOWN").str.upper()
        df["name"] = df.get("name", pd.Series(dtype=str)).fillna("N/A")
        df["domain"] = df.get("domain", pd.Series(dtype=str)).fillna("N/A")
        df["seller_id"] = df.get("seller_id", pd.Series(dtype=str)).fillna("N/A")
        if "is_confidential" not in df.columns:
            df["is_confidential"] = False
    return df, data.get("version", "N/A"), data.get("identifiers", []), data.get("contact_email", "")

def hostname(url):
    try: return urlparse(url).hostname or url
    except: return url

LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#666"),
    margin=dict(t=36, b=16, l=16, r=16),
    title_font=dict(color="#aaa", size=13, family="DM Sans"),
    xaxis=dict(gridcolor="#1a1a1a", linecolor="#1e1e1e", tickfont=dict(color="#555", size=11)),
    yaxis=dict(gridcolor="#1a1a1a", linecolor="#1e1e1e", tickfont=dict(color="#666", size=11)),
)

COLORS = {"PUBLISHER": "#1D9E75", "INTERMEDIARY": "#378ADD", "BOTH": "#EF9F27", "UNKNOWN": "#333"}

if "active_url" not in st.session_state:
    st.session_state["active_url"] = OGURY_URL

with st.sidebar:
    st.markdown('<div class="brand-tag">sellers.json</div>', unsafe_allow_html=True)
    st.markdown("## Analyzer")
    st.markdown('<div class="section-title">Source URL</div>', unsafe_allow_html=True)

    url_input = st.text_input("URL", value=st.session_state["active_url"], label_visibility="collapsed")

    if st.button("Analyze →", type="primary", use_container_width=True):
        st.session_state["active_url"] = url_input
        st.cache_data.clear()
        st.rerun()

    st.markdown('<div class="section-title">Quick access</div>', unsafe_allow_html=True)
    for label, url in QUICK_URLS:
        if st.button(f"↗  {label}", key=f"q_{label}", use_container_width=True):
            st.session_state["active_url"] = url
            st.cache_data.clear()
            st.rerun()

    st.markdown("---")
    if st.button("⟳  Refresh cache", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown(f'<div class="source-pill"><span class="green-dot"></span>{hostname(st.session_state["active_url"])}</div>', unsafe_allow_html=True)

active_url = st.session_state["active_url"]

st.markdown(f"""
<div style="padding:1.5rem 0 1rem 0; border-bottom:1px solid #1a1a1a; margin-bottom:1.5rem;">
    <div class="brand-tag">supply intelligence</div>
    <h1 class="page-title">Sellers.json Analyzer</h1>
    <p class="page-subtitle">Analyzing: <span style="font-family:DM Mono; color:#1D9E75; font-size:12px;">{active_url}</span></p>
</div>
""", unsafe_allow_html=True)

with st.spinner(f"Loading {hostname(active_url)}..."):
    try:
        df, version, identifiers, contact_email = load_sellers(active_url)
    except requests.exceptions.ConnectionError:
        st.markdown(f'<div class="err">⚠ Connection error — could not reach {active_url}</div>', unsafe_allow_html=True)
        st.stop()
    except requests.exceptions.HTTPError as e:
        st.markdown(f'<div class="err">⚠ HTTP {e}</div>', unsafe_allow_html=True)
        st.stop()
    except (json.JSONDecodeError, ValueError):
        st.markdown(f'<div class="err">⚠ Response is not valid JSON</div>', unsafe_allow_html=True)
        st.stop()
    except Exception as e:
        st.markdown(f'<div class="err">⚠ {e}</div>', unsafe_allow_html=True)
        st.stop()

if df.empty:
    st.warning("No sellers found in this file.")
    st.stop()

total = len(df)
publishers = len(df[df["seller_type"] == "PUBLISHER"])
intermediaries = len(df[df["seller_type"] == "INTERMEDIARY"])
both = len(df[df["seller_type"] == "BOTH"])
confidential = int(df["is_confidential"].sum()) if "is_confidential" in df.columns else 0

c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.metric("Total sellers", f"{total:,}")
with c2: st.metric("Publishers", f"{publishers:,}", f"{publishers/total*100:.1f}%")
with c3: st.metric("Intermediaries", f"{intermediaries:,}", f"{intermediaries/total*100:.1f}%")
with c4: st.metric("Both", f"{both:,}", f"{both/total*100:.1f}%")
with c5: st.metric("Version", str(version), f"{confidential} confidential")

st.markdown("<div style='margin:1.5rem 0; border-top:1px solid #1a1a1a;'></div>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Search & Filter", "Domain Analysis", "Raw data"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        tc = df["seller_type"].value_counts().reset_index()
        tc.columns = ["Type", "Count"]
        fig = go.Figure(go.Pie(
            labels=tc["Type"], values=tc["Count"], hole=0.55,
            marker=dict(colors=[COLORS.get(t, "#333") for t in tc["Type"]], line=dict(color="#0d0d0d", width=3)),
            textfont=dict(family="DM Sans", color="#aaa", size=12),
            textposition="outside", textinfo="percent+label"
        ))
        fig.update_layout(**LAYOUT, title="Type distribution", showlegend=False, height=300,
            annotations=[dict(text=f"<b>{total:,}</b>", x=0.5, y=0.5,
                font=dict(size=18, color="#ddd", family="DM Sans"), showarrow=False)])
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        fig2 = go.Figure()
        for _, row in tc.iterrows():
            fig2.add_trace(go.Bar(
                x=[row["Type"]], y=[row["Count"]], name=row["Type"],
                marker_color=COLORS.get(row["Type"], "#333"),
                text=[f"{row['Count']:,}"], textposition="outside",
                textfont=dict(color="#666", size=11)
            ))
        fig2.update_layout(**LAYOUT, title="Count by type", showlegend=False, height=300, bargap=0.4)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Top 25 domains</div>', unsafe_allow_html=True)
    dc = df[df["domain"] != "N/A"]["domain"].value_counts().head(25).reset_index()
    dc.columns = ["Domain", "Count"]
    fig3 = go.Figure(go.Bar(
        x=dc["Count"], y=dc["Domain"], orientation="h",
        marker=dict(color=dc["Count"], colorscale=[[0, "#0a2e22"], [0.5, "#0F6E56"], [1, "#5DCAA5"]]),
        text=dc["Count"], textposition="outside", textfont=dict(color="#555", size=11)
    ))
    fig3.update_layout(**LAYOUT, height=620,
        yaxis=dict(categoryorder="total ascending", tickfont=dict(color="#888", size=11), gridcolor="#1a1a1a"),
        xaxis=dict(gridcolor="#1a1a1a", tickfont=dict(color="#444")))
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    fc1, fc2, fc3 = st.columns([3, 1, 1])
    with fc1:
        q = st.text_input("Search", placeholder="Name, domain or seller ID...", label_visibility="collapsed")
    with fc2:
        tf = st.multiselect("Type", sorted(df["seller_type"].unique()), default=sorted(df["seller_type"].unique()), label_visibility="collapsed")
    with fc3:
        sb = st.selectbox("Sort", ["name", "domain", "seller_type"], label_visibility="collapsed")

    filt = df[df["seller_type"].isin(tf)].copy()
    if q:
        mask = (filt["name"].str.contains(q, case=False, na=False) |
                filt["domain"].str.contains(q, case=False, na=False) |
                filt["seller_id"].str.contains(q, case=False, na=False))
        filt = filt[mask]
    filt = filt.sort_values(sb).reset_index(drop=True)

    r1, r2 = st.columns([4, 1])
    with r1:
        st.markdown(f'<p class="stat-row">{len(filt):,} results</p>', unsafe_allow_html=True)
    with r2:
        st.download_button("⬇ Export CSV", filt.to_csv(index=False).encode(), "sellers_filtered.csv", use_container_width=True)

    cols = ["name", "domain", "seller_type", "seller_id"]
    if "is_confidential" in filt.columns:
        cols.append("is_confidential")
    st.dataframe(filt[cols], use_container_width=True, height=500,
        column_config={
            "name": st.column_config.TextColumn("Name", width="medium"),
            "domain": st.column_config.TextColumn("Domain", width="medium"),
            "seller_type": st.column_config.TextColumn("Type", width="small"),
            "seller_id": st.column_config.TextColumn("Seller ID", width="large"),
            "is_confidential": st.column_config.CheckboxColumn("Conf.", width="small"),
        })

with tab3:
    d1, d2 = st.columns(2)
    with d1:
        st.markdown('<div class="section-title">TLD distribution</div>', unsafe_allow_html=True)
        tld = df[df["domain"] != "N/A"]["domain"].str.extract(r'\.([a-zA-Z]{2,6})$')[0]
        tld_c = tld.value_counts().head(15).reset_index()
        tld_c.columns = ["TLD", "Count"]
        fig_t = go.Figure(go.Bar(
            x=tld_c["TLD"], y=tld_c["Count"],
            marker=dict(color=tld_c["Count"], colorscale=[[0, "#0a1e2e"], [1, "#378ADD"]]),
            text=tld_c["Count"], textposition="outside", textfont=dict(color="#555", size=11)
        ))
        fig_t.update_layout(**LAYOUT, height=340, showlegend=False)
        st.plotly_chart(fig_t, use_container_width=True)

    with d2:
        st.markdown('<div class="section-title">Type by TLD (top 10)</div>', unsafe_allow_html=True)
        df2 = df[df["domain"] != "N/A"].copy()
        df2["tld"] = df2["domain"].str.extract(r'\.([a-zA-Z]{2,6})$')[0]
        top10 = df2["tld"].value_counts().head(10).index
        tt = df2[df2["tld"].isin(top10)].groupby(["tld", "seller_type"]).size().reset_index(name="n")
        fig_tt = px.bar(tt, x="tld", y="n", color="seller_type", color_discrete_map=COLORS, barmode="stack")
        fig_tt.update_layout(**LAYOUT, height=340, showlegend=True,
            legend=dict(font=dict(color="#555", size=11, family="DM Sans"), bgcolor="rgba(0,0,0,0)",
                        orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
        st.plotly_chart(fig_tt, use_container_width=True)

    st.markdown('<div class="section-title">Domains with multiple seller IDs</div>', unsafe_allow_html=True)
    multi = df[df["domain"] != "N/A"].groupby("domain").agg(
        count=("seller_id", "count"),
        types=("seller_type", lambda x: " · ".join(sorted(x.unique())))
    ).reset_index().sort_values("count", ascending=False)
    multi = multi[multi["count"] > 1].reset_index(drop=True)
    st.markdown(f'<p class="stat-row">{len(multi):,} domains with 2+ seller IDs</p>', unsafe_allow_html=True)
    st.dataframe(multi.head(60), use_container_width=True, height=380,
        column_config={
            "domain": st.column_config.TextColumn("Domain"),
            "count": st.column_config.NumberColumn("# IDs", width="small"),
            "types": st.column_config.TextColumn("Types"),
        })

with tab4:
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<p class="stat-row">Version: {version}</p>', unsafe_allow_html=True)
    with m2:
        ids = ", ".join([f"{i.get('name')}: {i.get('value')}" for i in identifiers]) if identifiers else "—"
        st.markdown(f'<p class="stat-row">ID: {ids}</p>', unsafe_allow_html=True)
    with m3:
        if contact_email:
            st.markdown(f'<p class="stat-row">Contact: {contact_email}</p>', unsafe_allow_html=True)

    dl1, dl2 = st.columns([4, 1])
    with dl2:
        st.download_button("⬇ Export all CSV", df.to_csv(index=False).encode(), "sellers_full.csv", use_container_width=True)
    st.dataframe(df.reset_index(drop=True), use_container_width=True, height=580)

st.markdown(f"""
<div style="margin-top:3rem; padding-top:1rem; border-top:1px solid #1a1a1a;
     display:flex; justify-content:space-between;">
    <span style="font-family:DM Mono;font-size:10px;color:#2a2a2a;">sellers.json analyzer · 1h cache</span>
    <span style="font-family:DM Mono;font-size:10px;color:#2a2a2a;">{hostname(active_url)} · {total:,} sellers</span>
</div>
""", unsafe_allow_html=True)