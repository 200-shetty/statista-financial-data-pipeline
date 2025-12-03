import streamlit as st
import pandas as pd
from config import PROCESSED_DIR

CLEANED_CSV = PROCESSED_DIR / "financial_data_cleaned.csv"

st.set_page_config(page_title="Financial Data Explorer", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv(CLEANED_CSV)

df = load_data()

st.markdown(
    """
    <style>
    .main-title {
        font-size: 32px;
        font-weight: 700;
        color: #073B4C;
        margin-bottom: 20px;
    }
    
    .filter-label {
        font-size: 12px;
        font-weight: 700;
        color: #073B4C;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">Financial Data Explorer</div>', unsafe_allow_html=True)
st.markdown("### Filters")

if 'selected_countries' not in st.session_state:
    st.session_state.selected_countries = []
if 'selected_companies' not in st.session_state:
    st.session_state.selected_companies = []
if 'selected_industries' not in st.session_state:
    st.session_state.selected_industries = []
if 'selected_years' not in st.session_state:
    st.session_state.selected_years = []

filtered_data = df.copy()

filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns([2, 2, 2, 2, 1])

with filter_col1:
    st.markdown('<div class="filter-label">Country</div>', unsafe_allow_html=True)
    all_countries = sorted([str(x) for x in df["country"].dropna().unique() if pd.notna(x)])
    
    selected_countries = st.multiselect(
        "Country",
        options=all_countries,
        default=st.session_state.selected_countries if all(c in all_countries for c in st.session_state.selected_countries) else [],
        key="country_multiselect",
        label_visibility="collapsed"
    )
    st.session_state.selected_countries = selected_countries

if selected_countries:
    filtered_data = filtered_data[filtered_data["country"].isin(selected_countries)]

with filter_col2:
    st.markdown('<div class="filter-label">Company</div>', unsafe_allow_html=True)
    available_companies = sorted([str(x) for x in filtered_data["company_name"].dropna().unique() if pd.notna(x)])
    
    selected_companies = st.multiselect(
        "Company",
        options=available_companies,
        default=[c for c in st.session_state.selected_companies if c in available_companies],
        key="company_multiselect",
        label_visibility="collapsed"
    )
    st.session_state.selected_companies = selected_companies

if selected_companies:
    filtered_data = filtered_data[filtered_data["company_name"].isin(selected_companies)]

with filter_col3:
    st.markdown('<div class="filter-label">Industry</div>', unsafe_allow_html=True)
    available_industries = sorted([str(x) for x in filtered_data["industry"].dropna().unique() if pd.notna(x)])
    
    selected_industries = st.multiselect(
        "Industry",
        options=available_industries,
        default=[i for i in st.session_state.selected_industries if i in available_industries],
        key="industry_multiselect",
        label_visibility="collapsed"
    )
    st.session_state.selected_industries = selected_industries

if selected_industries:
    filtered_data = filtered_data[filtered_data["industry"].isin(selected_industries)]

with filter_col4:
    st.markdown('<div class="filter-label">Year</div>', unsafe_allow_html=True)
    available_years = sorted([int(y) for y in filtered_data["year"].dropna().unique() if pd.notna(y)])
    
    selected_years = st.multiselect(
        "Year",
        options=available_years,
        default=[y for y in st.session_state.selected_years if y in available_years],
        key="year_multiselect",
        label_visibility="collapsed"
    )
    st.session_state.selected_years = selected_years

if selected_years:
    filtered_data = filtered_data[filtered_data["year"].isin(selected_years)]

with filter_col5:
    st.markdown('<div class="filter-label" style="color: transparent;">.</div>', unsafe_allow_html=True)
    if st.button("Clear All", width="stretch", key="clear_button"):
        for key in ['country_multiselect', 'company_multiselect', 'industry_multiselect', 'year_multiselect']:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.selected_countries = []
        st.session_state.selected_companies = []
        st.session_state.selected_industries = []
        st.session_state.selected_years = []
        st.rerun()

filter_summary_parts = []
if selected_countries:
    filter_summary_parts.append(f"**Countries:** {', '.join(selected_countries[:2])}{'...' if len(selected_countries) > 2 else ''}")
if selected_companies:
    filter_summary_parts.append(f"**Companies:** {', '.join(selected_companies[:2])}{'...' if len(selected_companies) > 2 else ''}")
if selected_industries:
    filter_summary_parts.append(f"**Industries:** {', '.join(selected_industries[:2])}{'...' if len(selected_industries) > 2 else ''}")
if selected_years:
    filter_summary_parts.append(f"**Years:** {', '.join(map(str, sorted(selected_years)))}")

if filter_summary_parts:
    st.info(f"Active Filters: {' | '.join(filter_summary_parts)} | **{len(filtered_data):,} records** | **{filtered_data['company_name'].nunique()} companies**")
else:
    st.info(f"Showing all data | **{len(filtered_data):,} records** | **{filtered_data['company_name'].nunique()} companies**")

st.markdown("---")

display_col1, display_col2 = st.columns([5, 1])

with display_col2:
    csv = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="financial_data_filtered.csv",
        mime="text/csv",
        width="stretch"
    )


display_data = filtered_data.fillna("Not Reported")
st.dataframe(display_data, width="stretch", height="stretch")
st.markdown("### KPIs")
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.image(PROCESSED_DIR / "reports" / "kpi_margin_strength.png")

with col2:
    st.image(PROCESSED_DIR / "reports" / "kpi_profit_efficiency.png")

col3, col4 = st.columns(2)

with col3:
    st.image(PROCESSED_DIR / "reports" / "kpi_revenue_growth.png")

with col4:
    st.image(PROCESSED_DIR / "reports" / "kpi_roa.png")
st.markdown("---")
st.markdown("**Submitted by:** Gnanashri Kota Venkatesh")
