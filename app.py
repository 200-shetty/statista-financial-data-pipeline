import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pickle

st.set_page_config(page_title="Case Study: Extract and Prepare Data from a Public Source", layout="wide")

@st.cache_data
def load_data():
    try:
        with open('dataframe.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        st.error("dataframe.pkl not found")
        st.stop()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()

df = load_data()

required_columns = ['company_name', 'ticker', 'year', 'revenue']
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    st.error(f"Missing columns: {', '.join(missing_columns)}")
    st.stop()


STATISTA_TEAL = "#009E8C"
STATISTA_TEAL_LIGHT = "#6CCCC1"
STATISTA_BLUE = "#0F5B8A"
STATISTA_ORANGE = "#F9A03F"
STATISTA_RED = "#E94B3C"
STATISTA_NAVY = "#073B4C"
STATISTA_GRAY = "#6B7785"
BG_LIGHT = "#F7F9FA"


st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&display=swap');
    
    .stApp {{
        background-color: white;
        font-family: 'Lato', sans-serif;
    }}
    
    .main-title {{
        font-size: 32px;
        font-weight: 900;
        color: {STATISTA_NAVY};
        margin-bottom: 5px;
        line-height: 1.2;
    }}
    
    .subtitle {{
        font-size: 14px;
        color: {STATISTA_GRAY};
        margin-bottom: 20px;
        font-weight: 400;
    }}
    
    .section-header {{
        font-size: 20px;
        font-weight: 700;
        color: {STATISTA_NAVY};
        margin-top: 30px;
        margin-bottom: 15px;
        border-left: 4px solid {STATISTA_TEAL};
        padding-left: 12px;
    }}
    
    .filter-label {{
        font-size: 12px;
        font-weight: 700;
        color: {STATISTA_NAVY};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
    }}
    
    div[data-testid="stMetricValue"] {{
        font-size: 24px;
        font-weight: 900;
        color: {STATISTA_NAVY};
    }}
    
    div[data-testid="stMetricLabel"] {{
        font-size: 11px;
        color: {STATISTA_GRAY};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def format_usd(val):
    if pd.isna(val):
        return "n/a"
    if abs(val) >= 1e9:
        return f"${val/1e9:,.1f}B"
    if abs(val) >= 1e6:
        return f"${val/1e6:,.1f}M"
    if abs(val) >= 1e3:
        return f"${val/1e3:,.1f}K"
    return f"${val:,.0f}"

def format_percent(val):
    if pd.isna(val):
        return "n/a"
    return f"{val*100:.1f}%"

def parse_revenue(val):
    if pd.isna(val):
        return None
    
    if isinstance(val, (int, float)):
        return float(val)
    
    val_str = str(val).strip().upper()
    
    val_str = val_str.replace('$', '').replace('USD', '').strip()
    
    try:
        if 'B' in val_str:
            number = float(val_str.replace('B', '').strip())
            return number * 1e9
        elif 'M' in val_str:
            number = float(val_str.replace('M', '').strip())
            return number * 1e6
        elif 'K' in val_str:
            number = float(val_str.replace('K', '').strip())
            return number * 1e3
        else:
            return float(val_str)
    except:
        return None


st.markdown('<div class="main-title">Case Study: Extract and Prepare Data from a Public Source</div>', unsafe_allow_html=True)
st.markdown("### Filters")
if 'selected_countries' not in st.session_state:
    st.session_state.selected_countries = []
if 'selected_industries' not in st.session_state:
    st.session_state.selected_industries = []
if 'selected_tickers' not in st.session_state:
    st.session_state.selected_tickers = []
if 'selected_years' not in st.session_state:
    st.session_state.selected_years = []

filtered_data = df.copy()
filtered_data['revenue_numeric'] = filtered_data['revenue'].apply(parse_revenue)

filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns([2, 2, 3, 2, 1])

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

with filter_col3:
    st.markdown('<div class="filter-label">Company</div>', unsafe_allow_html=True)
    available_tickers_df = filtered_data[["ticker", "company_name"]].drop_duplicates().dropna()
    available_tickers = sorted(available_tickers_df["ticker"].unique().tolist())
    ticker_to_company = dict(zip(available_tickers_df["ticker"], available_tickers_df["company_name"]))
    
    ticker_display_options = [f"{t} - {ticker_to_company.get(t, 'Unknown')}" for t in available_tickers]
    ticker_display_map = {f"{t} - {ticker_to_company.get(t, 'Unknown')}": t for t in available_tickers}
    
    prev_selected_display = [
        f"{t} - {ticker_to_company.get(t, 'Unknown')}" 
        for t in st.session_state.selected_tickers 
        if t in available_tickers
    ]
    
    selected_tickers_display = st.multiselect(
        "Company",
        options=ticker_display_options,
        default=prev_selected_display,
        key="ticker_multiselect",
        label_visibility="collapsed"
    )
    
    selected_tickers = [ticker_display_map[display] for display in selected_tickers_display]
    st.session_state.selected_tickers = selected_tickers

if selected_tickers:
    filtered_data = filtered_data[filtered_data["ticker"].isin(selected_tickers)]

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
    if st.button("Clear All", use_container_width=True):
        st.session_state.selected_countries = []
        st.session_state.selected_industries = []
        st.session_state.selected_tickers = []
        st.session_state.selected_years = []
        st.rerun()

st.markdown('<div class="filter-label">Revenue Range</div>', unsafe_allow_html=True)

if "revenue_numeric" in filtered_data.columns and len(filtered_data) > 0:
    valid_revenues = filtered_data['revenue_numeric'].dropna()
    
    if not valid_revenues.empty and len(valid_revenues) > 0:
        min_revenue = float(valid_revenues.min())
        max_revenue = float(valid_revenues.max())
        
        if min_revenue < max_revenue:
            revenue_range = st.slider(
                "Revenue Range",
                min_value=min_revenue,
                max_value=max_revenue,
                value=(min_revenue, max_revenue),
                key="revenue_slider",
                label_visibility="collapsed"
            )
            
            st.caption(f"Selected range: {format_usd(revenue_range[0])} - {format_usd(revenue_range[1])}")
            
            filtered_data = filtered_data[
                (filtered_data['revenue_numeric'].isna()) | 
                ((filtered_data['revenue_numeric'] >= revenue_range[0]) & 
                 (filtered_data['revenue_numeric'] <= revenue_range[1]))
            ]
        else:
            st.info(f"Single revenue value: {format_usd(min_revenue)}")
    else:
        st.info("No valid revenue data available")
else:
    st.info("Revenue column not found")

data = filtered_data.drop(columns=['revenue_numeric'], errors='ignore')

filter_summary_parts = []
if selected_countries:
    filter_summary_parts.append(f"**Countries:** {', '.join(selected_countries[:2])}{'...' if len(selected_countries) > 2 else ''}")
if selected_industries:
    filter_summary_parts.append(f"**Industries:** {', '.join(selected_industries[:2])}{'...' if len(selected_industries) > 2 else ''}")
if selected_tickers:
    filter_summary_parts.append(f"**Companies:** {len(selected_tickers)} selected")
if selected_years:
    filter_summary_parts.append(f"**Years:** {', '.join(map(str, sorted(selected_years)))}")

if filter_summary_parts:
    st.info(f"Active Filters: {' | '.join(filter_summary_parts)} | **{len(data):,} records**")
else:
    st.info(f"Showing all data | **{len(data):,} records** | **{data['company_name'].nunique()} companies**")

st.markdown("---")
st.markdown('<div class="section-header">Data Table</div>', unsafe_allow_html=True)
display_col1, display_col2 = st.columns([5, 1])

with display_col2:
    csv = data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="financial_data_filtered.csv",
        mime="text/csv",
        use_container_width=True
    )

display_data = data.astype(str).replace('nan', 'Not Reported').replace('None', 'Not Reported').replace('<NA>', 'Not Reported')

st.dataframe(
    display_data.reset_index(drop=True),
    width="stretch",
    height=500
)

st.markdown("---")

if not data.empty:
    st.markdown('<div class="section-header">Key Metrics Overview</div>', unsafe_allow_html=True)
    
    total_companies = data['company_name'].nunique()
    total_records = len(data)
    
    latest_year = data['year'].max()
    latest_data = data[data['year'] == latest_year]
    
    avg_revenue = data['revenue'].apply(parse_revenue).mean()
    avg_roa = data['ROA'].mean() if 'ROA' in data.columns else None
    avg_roe = data['roe'].mean() if 'roe' in data.columns else None
    avg_npm = data['net_profit_margin'].mean() if 'net_profit_margin' in data.columns else None
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5, kpi_col6 = st.columns(6)
    
    with kpi_col1:
        st.metric("Companies", f"{total_companies}")
    
    with kpi_col2:
        st.metric("Avg Revenue", format_usd(avg_revenue) if pd.notna(avg_revenue) else "n/a")
    
    with kpi_col3:
        st.metric("Avg ROA", format_percent(avg_roa) if pd.notna(avg_roa) else "n/a")
    
    with kpi_col4:
        st.metric("Avg ROE", format_percent(avg_roe) if pd.notna(avg_roe) else "n/a")
    
    with kpi_col5:
        st.metric("Avg Net Margin", f"{avg_npm:.1f}%" if pd.notna(avg_npm) else "n/a")
    
    with kpi_col6:
        st.metric("Latest Year", f"{int(latest_year)}" if pd.notna(latest_year) else "n/a")
