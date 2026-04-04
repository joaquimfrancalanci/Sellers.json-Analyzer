import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime

st.set_page_config(
    page_title="Sellers.json Analyzer",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for boxes and cards
st.markdown("""
<style>
    .metric-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }
    .metric-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-color: #c0c0c0;
    }
    .metric-card .metric-label {
        font-size: 13px;
        color: #666;
        margin-bottom: 8px;
        font-weight: 500;
    }
    .metric-card .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #1f2937;
        line-height: 1.2;
    }
    .selection-box {
        background: #ffffff;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        border: 1px solid #e0e0e0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    table { width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 0.5rem; }
    thead tr { background: #f8f9fa; border-bottom: 2px solid #e0e0e0; }
    thead th { padding: 10px 14px; text-align: left; font-weight: 600; color: #444; font-size: 13px; }
    tbody tr { border-bottom: 1px solid #f0f0f0; }
    tbody tr:hover { background: #fafafa; }
    tbody td { padding: 8px 14px; color: #333; vertical-align: middle; }
    .feedback-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.2rem;
        color: white;
        margin-top: 1rem;
        text-align: center;
    }
    .feedback-button {
        background-color: white;
        color: #764ba2;
        border: none;
        border-radius: 30px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 16px;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        display: inline-block;
        margin-top: 0.5rem;
    }
    .feedback-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .stButton button {
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

TYPE_COLORS = {
    "BOTH":         "#22c55e",
    "PUBLISHER":    "#06b6d4",
    "INTERMEDIARY": "#f8dcca",
    "UNKNOWN":      "#888780",
}

SOURCES = {
    "Ogury": "https://sellers.ogury.com/",
    "Pubmatic": "https://cdn.pubmatic.com/sellers/data/sellers.json",
    "Teads": "https://sellers.teads.tv/sellers.json",
}

@st.cache_data(ttl=3600)
def load_data(url: str):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; SellersJsonAnalyzer/1.0)"}
    resp = requests.get(url, timeout=15, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    sellers = data.get("sellers", [])
    df = pd.DataFrame(sellers)
    df["seller_type"] = df["seller_type"].fillna("UNKNOWN")
    df["name"] = df["name"].fillna("N/A")
    df["domain"] = df["domain"].fillna("N/A")
    if "is_confidential" not in df.columns:
        df["is_confidential"] = False
    return df, data.get("version"), data.get("identifiers", [])

st.title("📊 Sellers.json Analyzer")

# Sidebar for Controls and Feedback
with st.sidebar:
    
    # Selection box for source
    with st.container():
        st.markdown("### 📡 Data Source Selection")
        selected_source = st.selectbox(
            "Choose sellers.json source",
            options=list(SOURCES.keys()),
            help="Select the adtech platform to analyze"
        )
        if st.button("🔄 Refresh Data", type="secondary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Additional selection box for analysis options
    with st.container():
        st.markdown("### 📊 Analysis Options")
        top_n_domains = st.selectbox(
            "Top domains to display",
            options=[10, 20, 30, 50],
            index=1,
            help="Number of top domains shown in the overview"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Feedback Section with button link to Google Form
    st.markdown("---")
    st.markdown('<div class="feedback-card">', unsafe_allow_html=True)
    st.markdown("### 💬 Send Feedback")
    st.markdown("Help us improve the Sellers.json Analyzer!")
    st.markdown("Rate the app and share your suggestions (only @ogury.co emails).")
    
    # Google Form URL (your published form)
    GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSe0Go2SeI3R_ceb9ekeX285dKvfHip9pM_KAtDngjNkiis1eQ/viewform?usp=pp_url"
    
    # Create a button that opens the form in a new tab
    st.markdown(f"""
    <a href="{GOOGLE_FORM_URL}" target="_blank">
        <button class="feedback-button">
            📝 Open Feedback Form
        </button>
    </a>
    """, unsafe_allow_html=True)
    
    st.caption("Opens in a new tab. Your responses go directly to the admin.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.caption(f"📌 Admin: joaquim.francalanci@ogury.co")

# Main content area
active_url = SOURCES[selected_source]
st.caption(f"**Active Source:** {active_url}")

with st.spinner(f"Loading {selected_source} sellers.json..."):
    try:
        df, version, identifiers = load_data(active_url)
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error loading {selected_source}: {e}")
        st.stop()
    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to {active_url}. Check your internet connection.")
        st.stop()
    except Exception as e:
        st.error(f"Failed to load sellers.json: {e}")
        st.stop()

if df.empty:
    st.warning("No sellers found in this file.")
    st.stop()

st.markdown("---")

# KPI metrics displayed in styled boxes (border + background)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Total Sellers</div>
        <div class="metric-value">{:,}</div>
    </div>
    """.format(len(df)), unsafe_allow_html=True)

with col2:
    publishers = len(df[df["seller_type"] == "PUBLISHER"])
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Publishers</div>
        <div class="metric-value">{:,}</div>
    </div>
    """.format(publishers), unsafe_allow_html=True)

with col3:
    intermediaries = len(df[df["seller_type"] == "INTERMEDIARY"])
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Intermediaries</div>
        <div class="metric-value">{:,}</div>
    </div>
    """.format(intermediaries), unsafe_allow_html=True)

with col4:
    both = len(df[df["seller_type"] == "BOTH"])
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Both</div>
        <div class="metric-value">{:,}</div>
    </div>
    """.format(both), unsafe_allow_html=True)

st.markdown("---")

# Tabs panel
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🔍 Search & Filter", "🌐 Domain Analysis", "📋 Raw Data"])

with tab1:
    col_a, col_b = st.columns(2)

    with col_a:
        type_counts = df["seller_type"].value_counts().reset_index()
        type_counts.columns = ["Seller Type", "Count"]
        fig_pie = px.pie(
            type_counts,
            names="Seller Type",
            values="Count",
            title="Seller Type Distribution",
            color="Seller Type",
            color_discrete_map=TYPE_COLORS,
            hole=0.4
        )
        fig_pie.update_traces(textposition="outside", textinfo="percent+label")
        fig_pie.update_layout(showlegend=False, height=380)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        fig_bar = px.bar(
            type_counts,
            x="Seller Type",
            y="Count",
            title="Seller Count by Type",
            color="Seller Type",
            color_discrete_map=TYPE_COLORS,
            text="Count"
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(showlegend=False, height=380, yaxis_title="Count")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader(f"Top {top_n_domains} Domains by Seller Count")
    domain_counts = df[df["domain"] != "N/A"]["domain"].value_counts().head(top_n_domains).reset_index()
    domain_counts.columns = ["Domain", "Count"]
    fig_domains = px.bar(
        domain_counts,
        x="Count",
        y="Domain",
        orientation="h",
        color="Count",
        color_continuous_scale=["#9FE1CB", "#0F6E56"],
        title=f"Top {top_n_domains} Domains"
    )
    fig_domains.update_layout(height=550, yaxis={"categoryorder": "total ascending"}, coloraxis_showscale=False)
    st.plotly_chart(fig_domains, use_container_width=True)

with tab2:
    st.subheader("Search & Filter Sellers")
    
    # Selection box for filters
    with st.container():
        
        col_f1, col_f2, col_f3 = st.columns([2, 1, 1])
        with col_f1:
            search_query = st.text_input("🔍 Search by name, domain or seller ID", placeholder="e.g. Google, publisher.com...")
        with col_f2:
            type_filter = st.multiselect("Seller Type", options=sorted(df["seller_type"].unique()), default=sorted(df["seller_type"].unique()))
        with col_f3:
            sort_by = st.selectbox("Sort by", ["name", "domain", "seller_type", "seller_id"])
        st.markdown('</div>', unsafe_allow_html=True)

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
            "BOTH": "background:#d4f5e2;color:#0a5c35",
            "PUBLISHER": "background:#cff4fc;color:#0c5460",
            "INTERMEDIARY": "background:#e8f8ee;color:#1a6b3a",
        }.get(t, "background:#f0f0f0;color:#666")
        return f'<span style="display:inline-block;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:600;{css}">{t}</span>'

    display_df = filtered[["name", "domain", "seller_type", "seller_id"]].copy().reset_index(drop=True)
    display_df["seller_type"] = display_df["seller_type"].apply(tag_html)

    st.write(
        display_df.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered results as CSV",
        csv,
        f"{selected_source.lower()}_sellers_filtered.csv",
        "text/csv"
    )

with tab3:
    st.subheader("Domain Analysis")
    
    # Selection box for domain analysis options
    with st.container():
        
        col_d_opt1, col_d_opt2 = st.columns(2)
        with col_d_opt1:
            top_tlds_to_show = st.selectbox("Number of TLDs to display", [10, 15, 20, 25], index=1)
        with col_d_opt2:
            show_multi_domain_threshold = st.number_input("Minimum seller IDs per domain", min_value=1, max_value=10, value=2, step=1)
        st.markdown('</div>', unsafe_allow_html=True)

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        st.markdown("**Top Level Domain (TLD) Distribution**")
        tld_series = df[df["domain"] != "N/A"]["domain"].dropna().str.extract(r'\.([a-zA-Z]{2,6})$')[0]
        tld_counts = tld_series.value_counts().head(top_tlds_to_show).reset_index()
        tld_counts.columns = ["TLD", "Count"]
        fig_tld = px.bar(
            tld_counts,
            x="TLD",
            y="Count",
            color="Count",
            color_continuous_scale=["#9FE1CB", "#0F6E56"],
            title=f"Top {top_tlds_to_show} TLDs"
        )
        fig_tld.update_layout(coloraxis_showscale=False, height=380)
        st.plotly_chart(fig_tld, use_container_width=True)

    with col_d2:
        st.markdown("**Seller Type by TLD (Top 10)**")
        df_tld = df[df["domain"] != "N/A"].copy()
        df_tld["tld"] = df_tld["domain"].str.extract(r'\.([a-zA-Z]{2,6})$')[0]
        top_tlds = df_tld["tld"].value_counts().head(10).index
        df_tld_top = df_tld[df_tld["tld"].isin(top_tlds)]
        tld_type = df_tld_top.groupby(["tld", "seller_type"]).size().reset_index(name="count")
        fig_tld_type = px.bar(
            tld_type,
            x="tld",
            y="count",
            color="seller_type",
            color_discrete_map=TYPE_COLORS,
            title="Seller Type by TLD",
            barmode="stack"
        )
        fig_tld_type.update_layout(height=380, xaxis_title="TLD", yaxis_title="Count")
        st.plotly_chart(fig_tld_type, use_container_width=True)

    st.subheader(f"Domains with {show_multi_domain_threshold}+ Seller IDs")
    multi_domain = df[df["domain"] != "N/A"].groupby("domain").agg(
        seller_count=("seller_id", "count"),
        seller_types=("seller_type", lambda x: ", ".join(sorted(x.unique())))
    ).reset_index().sort_values("seller_count", ascending=False)
    multi_domain = multi_domain[multi_domain["seller_count"] >= show_multi_domain_threshold]

    st.markdown(f"**{len(multi_domain):,}** domains with {show_multi_domain_threshold}+ seller IDs")
    st.dataframe(
        multi_domain.head(50).reset_index(drop=True),
        use_container_width=True,
        height=350,
        column_config={
            "domain": st.column_config.TextColumn("Domain", width="medium"),
            "seller_count": st.column_config.NumberColumn("# Seller IDs", width="small"),
            "seller_types": st.column_config.TextColumn("Types", width="medium"),
        }
    )

with tab4:
    st.subheader("Raw Data")
    st.markdown(f"**Version:** {version} | **Identifiers:** {identifiers}")
    st.dataframe(
        df.reset_index(drop=True),
        use_container_width=True,
        height=600
    )
    csv_all = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download full sellers.json as CSV",
        csv_all,
        f"{selected_source.lower()}_sellers_full.csv",
        "text/csv"
    )

st.markdown("---")
st.caption(f"Data loaded live from {active_url} · Cached for 1 hour · Built with Streamlit")
st.caption("💡 Tip: Use the sidebar to change data source, analysis options, or click 'Open Feedback Form' to share your thoughts.")