import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import re
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Startup Funding Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CUSTOM CSS FOR PROFESSIONAL STYLING
# =============================================================================
st.markdown("""
<style>
    /* Main header */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 1.6rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 1.5rem 0 0.8rem 0;
        border-bottom: 2px solid #eaeef2;
        padding-bottom: 0.3rem;
    }
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 18px 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: transform 0.2s;
        margin-bottom: 10px;
    }
    .metric-card:hover {
        transform: translateY(-3px);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.95rem;
        opacity: 0.85;
        margin: 4px 0 0 0;
        font-weight: 500;
    }
    .metric-sub {
        font-size: 0.8rem;
        opacity: 0.7;
        margin: 0;
    }
    /* Section containers */
    .section-container {
        background: #f8fafc;
        border-radius: 12px;
        padding: 20px 25px;
        margin-bottom: 25px;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .insight-box {
        background: #ffffff;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        margin-bottom: 15px;
    }
    /* Download button */
    .download-btn {
        background: #28a745;
        color: white;
        border: none;
        padding: 8px 20px;
        border-radius: 6px;
        font-weight: 500;
        cursor: pointer;
        transition: background 0.2s;
    }
    .download-btn:hover {
        background: #218838;
    }
    /* Responsive tweaks */
    @media (max-width: 768px) {
        .main-header { font-size: 2rem; }
        .metric-value { font-size: 1.6rem; }
        .metric-card { padding: 12px; }
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA LOADING AND PREPROCESSING (CACHED)
# =============================================================================
@st.cache_data
def load_data():
    """Load and preprocess the startup funding datasets."""
    try:
        df = pd.read_csv('startupfundingclean.csv')
        original = pd.read_csv('dforiginal.csv')
    except FileNotFoundError:
        st.error("Dataset files not found. Please ensure 'startupfundingclean.csv' and 'dforiginal.csv' are in the app directory.")
        st.stop()
    
    # ---------- Clean investors ----------
    df['investors'] = df['investors'].astype(str).str.replace(r'\\n|\n|\\x[a-fA-F0-9]{2}|\\', '', regex=True)
    df['investors'] = df['investors'].str.strip()
    
    # ---------- Process funding round stages ----------
    df['round'] = df['round'].str.replace('\\\\n', '').str.replace('/', ',').str.lower().str.strip()
    
    # Stage mapping (expanded)
    stage_mapping = {
        # Seed Stage
        'pre-series a': 'Seed Stage', 'pre series a': 'Seed Stage',
        'seed round': 'Seed Stage', 'seed': 'Seed Stage', 'seed funding': 'Seed Stage',
        'seed funding round': 'Seed Stage', 'seedfunding': 'Seed Stage',
        'angel': 'Seed Stage', 'angel round': 'Seed Stage', 'angel funding': 'Seed Stage',
        'seed, angel funding': 'Seed Stage', 'seed , angel funding': 'Seed Stage',
        'seed,angel funding': 'Seed Stage', 'seed , angle funding': 'Seed Stage',
        'angel , seed funding': 'Seed Stage', 'bridge round': 'Seed Stage',
        'crowd funding': 'Seed Stage', 'maiden round': 'Seed Stage',
        # Early Growth
        'series a': 'Early Growth Stage', 'series b': 'Early Growth Stage',
        'series b (extension)': 'Early Growth Stage',
        # Growth Stage
        'series c': 'Growth Stage', 'series d': 'Growth Stage',
        # Late Stage
        'series e': 'Late Stage', 'series f': 'Late Stage', 'series g': 'Late Stage',
        'series h': 'Late Stage', 'series j': 'Late Stage', 'private equity': 'Late Stage',
        'private equity round': 'Late Stage', 'privateequity': 'Late Stage',
        'private': 'Late Stage', 'private funding': 'Late Stage',
        # Debt Stage
        'debt': 'Debt Stage', 'debt funding': 'Debt Stage', 'debt-funding': 'Debt Stage',
        'debt and preference capital': 'Debt Stage', 'structured debt': 'Debt Stage',
        'term loan': 'Debt Stage', 'mezzanine': 'Debt Stage',
        # Venture Stage
        'venture': 'Venture Stage', 'single venture': 'Venture Stage',
        'venture round': 'Venture Stage', 'venture - series unknown': 'Venture Stage',
        'corporate round': 'Venture Stage', 'funding round': 'Venture Stage',
        'equity': 'Venture Stage', 'equity based funding': 'Venture Stage',
        'inhouse funding': 'Venture Stage',
        # Other
        'undisclosed': 'Other'
    }
    df['stage'] = df['round'].map(stage_mapping).fillna('Other')
    
    # ---------- Startup name cleaning ----------
    df['startup'] = df['startup'].str.replace("BYJU's", "Byju's")
    df['city'] = df['city'].str.replace('Bangalore', 'Bengaluru')
    
    # ---------- Date processing ----------
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['month_year'] = df['date'].dt.to_period('M').astype(str)
    df['quarter'] = df['date'].dt.quarter
    df['year_quarter'] = df['date'].dt.to_period('Q').astype(str)
    
    # ---------- Additional derived metrics ----------
    # Total funding per startup (for leaderboards)
    startup_total = df.groupby('startup')['amount'].sum().reset_index(name='total_funding')
    df = df.merge(startup_total, on='startup', how='left')
    
    # Number of rounds per startup
    rounds_count = df.groupby('startup').size().reset_index(name='rounds_count')
    df = df.merge(rounds_count, on='startup', how='left')
    
    # Round number per startup (1st, 2nd, etc.)
    df['round_number'] = df.groupby('startup').cumcount() + 1
    
    # Drop rows with zero/negative amounts (if any)
    df = df[df['amount'] > 0]
    
    # Original dataset may have different columns; we'll keep it as is for some KPIs
    # but we'll use df for most analysis.
    return df, original

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def format_currency(value):
    """Format currency in Crores with Indian numbering."""
    if pd.isna(value):
        return "N/A"
    return f"₹{value:,.0f} Cr"

def format_number(value):
    """Format large numbers with commas."""
    if pd.isna(value):
        return "N/A"
    return f"{value:,.0f}"

def create_metric_card(title, value, subtitle="", color_gradient=True):
    """Return HTML for a metric card."""
    gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" if color_gradient else "#2c3e50"
    return f"""
    <div class="metric-card" style="background: {gradient};">
        <p class="metric-label">{title}</p>
        <h3 class="metric-value">{value}</h3>
        <p class="metric-sub">{subtitle}</p>
    </div>
    """

def get_yoy_growth(df, column='amount', freq='Y'):
    """Calculate year-over-year growth percentage."""
    grouped = df.groupby('year')[column].sum().reset_index()
    grouped['growth'] = grouped[column].pct_change() * 100
    return grouped

# =============================================================================
# DASHBOARD: OVERALL ANALYSIS
# =============================================================================
def overall_analysis(df, original):
    st.markdown('<div class="main-header">📊 Startup Funding Analytics</div>', unsafe_allow_html=True)
    st.markdown("#### Executive Summary of Indian Startup Ecosystem")
    
    # ---- Top KPIs ----
    total_funding = original['amount'].sum()
    peak_funding = original['amount'].max()
    avg_funding = original['amount'].mean()
    total_startups = df['startup'].nunique()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(create_metric_card("Total Funding", format_currency(total_funding), "Cumulative investment"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Peak Funding", format_currency(peak_funding), "Largest single round"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("Average Round", format_currency(avg_funding), "Per funding round"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("Startups Funded", format_number(total_startups), "Unique companies"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ---- YoY Growth ----
    st.markdown('<div class="sub-header">📈 Year-over-Year Growth</div>', unsafe_allow_html=True)
    yoy_data = get_yoy_growth(df)
    fig = px.bar(yoy_data, x='year', y='amount', text='growth', 
                 title="Yearly Funding & Growth %",
                 labels={'amount': 'Funding (Cr)', 'year': 'Year'},
                 color='growth', color_continuous_scale='RdYlGn')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig, use_container_width=True)
    
    # ---- Funding Trends (Monthly & Quarterly) ----
    col1, col2 = st.columns(2)
    with col1:
        monthly = df.groupby('month_year')['amount'].sum().reset_index()
        fig = px.area(monthly, x='month_year', y='amount', 
                     title="Monthly Funding Trend", 
                     labels={'amount': 'Funding (Cr)', 'month_year': 'Month'})
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        quarterly = df.groupby('year_quarter')['amount'].sum().reset_index()
        fig = px.bar(quarterly, x='year_quarter', y='amount',
                    title="Quarterly Funding Distribution",
                    labels={'amount': 'Funding (Cr)', 'year_quarter': 'Quarter'})
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # ---- Funding Funnel (by Stage) ----
    st.markdown('<div class="sub-header">🔽 Funding Funnel by Stage</div>', unsafe_allow_html=True)
    stage_funding = df.groupby('stage')['amount'].sum().reset_index()
    # Order stages logically
    stage_order = ['Seed Stage', 'Early Growth Stage', 'Growth Stage', 'Late Stage', 'Debt Stage', 'Venture Stage', 'Other']
    stage_funding['stage'] = pd.Categorical(stage_funding['stage'], categories=stage_order, ordered=True)
    stage_funding = stage_funding.sort_values('stage')
    
    fig = go.Figure(go.Funnel(
        y=stage_funding['stage'],
        x=stage_funding['amount'],
        textinfo="value+percent previous",
        marker=dict(color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"])
    ))
    fig.update_layout(title="Total Funding Amount by Stage", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # ---- Geographic & Sector Analysis ----
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🏙️ Top Cities by Funding")
        city_funding = df.groupby('city')['amount'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(x=city_funding.values, y=city_funding.index, orientation='h',
                     labels={'x': 'Funding (Cr)', 'y': 'City'},
                     text=city_funding.values,
                     color=city_funding.values, color_continuous_scale='Blues')
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🌐 Sector Funding Treemap")
        sector_funding = df.groupby('vertical')['amount'].sum().reset_index()
        sector_funding = sector_funding.sort_values('amount', ascending=False).head(15)
        fig = px.treemap(sector_funding, path=['vertical'], values='amount',
                         title="Sector-wise Funding Distribution",
                         color='amount', color_continuous_scale='Tealgrn')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # ---- Funding Heatmap (City x Year) ----
    st.markdown('<div class="sub-header">🗺️ City vs Year Funding Heatmap</div>', unsafe_allow_html=True)
    heatmap_data = df.pivot_table(index='city', columns='year', values='amount', aggfunc='sum').fillna(0)
    # Limit to top cities
    top_cities = df.groupby('city')['amount'].sum().sort_values(ascending=False).head(15).index
    heatmap_data = heatmap_data.loc[top_cities]
    
    fig = px.imshow(heatmap_data, 
                    labels=dict(x="Year", y="City", color="Funding (Cr)"),
                    aspect="auto", 
                    color_continuous_scale='Viridis')
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # ---- Leaderboards ----
    st.markdown('<div class="sub-header">🏆 Leaderboards</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Top 10 Startups by Funding")
        top_startups = df.groupby('startup')['amount'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(x=top_startups.values, y=top_startups.index, orientation='h',
                     text=top_startups.values,
                     color=top_startups.values, color_continuous_scale='Green')
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Top 10 Investors by Funding")
        top_investors = df.groupby('investors')['amount'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(x=top_investors.values, y=top_investors.index, orientation='h',
                     text=top_investors.values,
                     color=top_investors.values, color_continuous_scale='Orange')
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# DASHBOARD: STARTUP ANALYSIS
# =============================================================================
def startup_analysis(df):
    st.markdown('<div class="main-header">🚀 Startup Deep Dive</div>', unsafe_allow_html=True)
    
    # Startup selector
    startup_options = sorted(df['startup'].unique().tolist())
    selected_startup = st.selectbox("Select a Startup", startup_options, key='startup_select')
    
    if not selected_startup:
        st.info("Please select a startup to view detailed analysis.")
        return
    
    startup_df = df[df['startup'] == selected_startup].copy()
    if startup_df.empty:
        st.warning("No data available for this startup.")
        return
    
    # ---- Overview KPIs ----
    total_funding = startup_df['amount'].sum()
    avg_round = startup_df['amount'].mean()
    rounds_count = len(startup_df)
    latest_round = startup_df['date'].max().strftime('%b %Y') if not startup_df.empty else 'N/A'
    top_investor = startup_df['investors'].value_counts().index[0] if not startup_df.empty else 'N/A'
    industry = startup_df['vertical'].iloc[0] if not startup_df.empty else 'N/A'
    sub_industry = startup_df['subvertical'].iloc[0] if not startup_df.empty else 'N/A'
    city = startup_df['city'].iloc[0] if not startup_df.empty else 'N/A'
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(create_metric_card("Total Funding", format_currency(total_funding), "Cumulative"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Rounds", format_number(rounds_count), "Funding rounds"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("Latest Round", latest_round, "Most recent funding"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("Top Investor", top_investor[:25] + "..." if len(top_investor)>25 else top_investor, "Most frequent"), unsafe_allow_html=True)
    
    # ---- Company Info ----
    with st.expander("Company Profile", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Industry:** {industry}")
            st.write(f"**Sub-industry:** {sub_industry}")
            st.write(f"**Headquarters:** {city}")
        with col2:
            st.write(f"**First Funding:** {startup_df['date'].min().strftime('%b %Y') if not startup_df.empty else 'N/A'}")
            st.write(f"**Stages Involved:** {', '.join(startup_df['stage'].unique()) if not startup_df.empty else 'N/A'}")
            st.write(f"**Unique Investors:** {startup_df['investors'].nunique() if not startup_df.empty else 'N/A'}")
    
    # ---- Funding Timeline ----
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Funding Timeline")
        timeline = startup_df.sort_values('date')
        fig = px.line(timeline, x='date', y='amount', markers=True,
                     labels={'amount': 'Funding (Cr)', 'date': 'Date'},
                     title=f"{selected_startup} Funding Rounds")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Round Distribution")
        round_dist = startup_df['round'].value_counts().reset_index()
        round_dist.columns = ['Round', 'Count']
        fig = px.bar(round_dist, x='Count', y='Round', orientation='h',
                    text='Count',
                    labels={'Count': 'Number of Rounds', 'Round': 'Round Type'})
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # ---- Investor Participation ----
    st.markdown("#### Investor Participation")
    inv_participation = startup_df['investors'].value_counts().reset_index()
    inv_participation.columns = ['Investor', 'Number of Rounds']
    inv_participation['Total Investment'] = inv_participation['Investor'].apply(
        lambda x: startup_df[startup_df['investors'] == x]['amount'].sum()
    )
    st.dataframe(inv_participation, use_container_width=True, hide_index=True)
    
    # ---- Similar Startups (based on industry and city) ----
    st.markdown("#### Similar Startups")
    similar_criteria = (df['vertical'] == industry) & (df['city'] == city) & (df['startup'] != selected_startup)
    similar = df[similar_criteria][['startup', 'amount', 'rounds_count']].drop_duplicates('startup').head(5)
    if not similar.empty:
        st.dataframe(similar, use_container_width=True, hide_index=True)
    else:
        st.info("No similar startups found based on industry and city.")
    
    # ---- Download ----
    csv = startup_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Startup Report (CSV)",
        data=csv,
        file_name=f"{selected_startup}_funding_report.csv",
        mime="text/csv",
        key='startup_download'
    )

# =============================================================================
# DASHBOARD: INVESTOR ANALYSIS
# =============================================================================
def investor_analysis(df):
    st.markdown('<div class="main-header">💰 Investor Intelligence</div>', unsafe_allow_html=True)
    
    # Investor selector
    investor_options = sorted(df['investors'].dropna().unique().tolist())
    selected_investor = st.selectbox("Select an Investor", investor_options, key='investor_select')
    
    if not selected_investor:
        st.info("Please select an investor to view detailed analysis.")
        return
    
    # Filter investments containing the investor name (partial match)
    investor_df = df[df['investors'].str.contains(selected_investor, na=False, regex=False)].copy()
    if investor_df.empty:
        st.warning("No investments found for this investor.")
        return
    
    # ---- Overview KPIs ----
    total_investments = len(investor_df)
    total_funding = investor_df['amount'].sum()
    avg_investment = investor_df['amount'].mean()
    portfolio_companies = investor_df['startup'].nunique()
    biggest_investment = investor_df['amount'].max()
    preferred_round = investor_df['round'].mode()[0] if not investor_df.empty else 'N/A'
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(create_metric_card("Portfolio Size", format_number(portfolio_companies), "Unique startups"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Total Funding", format_currency(total_funding), "All investments"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("Avg Deal Size", format_currency(avg_investment), "Per round"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("Preferred Round", preferred_round[:20] + "..." if len(preferred_round)>20 else preferred_round, "Most frequent"), unsafe_allow_html=True)
    
    # ---- Additional KPIs ----
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(create_metric_card("Biggest Investment", format_currency(biggest_investment), "Largest single deal"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Total Deals", format_number(total_investments), "Number of rounds"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("Diversity Score", f"{investor_df['vertical'].nunique()} sectors", "Industries covered"), unsafe_allow_html=True)
    
    # ---- Investment Timeline ----
    st.markdown("#### Investment Activity Over Time")
    col1, col2 = st.columns(2)
    with col1:
        yearly = investor_df.groupby('year')['amount'].sum().reset_index()
        fig = px.line(yearly, x='year', y='amount', markers=True,
                     labels={'amount': 'Investment (Cr)', 'year': 'Year'},
                     title="Yearly Investment Trend")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        # Monthly trend
        monthly = investor_df.groupby('month_year')['amount'].sum().reset_index()
        fig = px.bar(monthly, x='month_year', y='amount',
                    labels={'amount': 'Investment (Cr)', 'month_year': 'Month'},
                    title="Monthly Investment Distribution")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # ---- Sector & Stage Allocation ----
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Sector Allocation")
        sector = investor_df['vertical'].value_counts().reset_index()
        sector.columns = ['Sector', 'Count']
        fig = px.treemap(sector, path=['Sector'], values='Count',
                         title="Investments by Sector",
                         color='Count', color_continuous_scale='Blues')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Stage Allocation")
        stage = investor_df['stage'].value_counts().reset_index()
        stage.columns = ['Stage', 'Count']
        fig = px.bar(stage, x='Count', y='Stage', orientation='h',
                    text='Count',
                    labels={'Count': 'Number of Investments', 'Stage': 'Stage'},
                    color='Count', color_continuous_scale='Oranges')
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # ---- Geographic Allocation ----
    st.markdown("#### City-wise Distribution")
    city = investor_df['city'].value_counts().reset_index().head(10)
    city.columns = ['City', 'Count']
    fig = px.bar(city, x='Count', y='City', orientation='h',
                text='Count',
                labels={'Count': 'Number of Investments', 'City': 'City'},
                color='Count', color_continuous_scale='Greens')
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # ---- Top Investments ----
    st.markdown("#### Top 5 Investments")
    top_inv = investor_df.nlargest(5, 'amount')[['startup', 'amount', 'round', 'date', 'vertical']]
    top_inv['date'] = top_inv['date'].dt.strftime('%Y-%m-%d')
    st.dataframe(top_inv, use_container_width=True, hide_index=True)
    
    # ---- Portfolio Companies ----
    st.markdown("#### Portfolio Companies")
    portfolio = investor_df[['startup', 'amount', 'round', 'date', 'vertical', 'city']].drop_duplicates('startup')
    portfolio['date'] = portfolio['date'].dt.strftime('%Y-%m-%d')
    st.dataframe(portfolio, use_container_width=True, hide_index=True)
    
    # ---- Download ----
    csv = investor_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Investor Report (CSV)",
        data=csv,
        file_name=f"{selected_investor}_portfolio_report.csv",
        mime="text/csv",
        key='investor_download'
    )

# =============================================================================
# SIDEBAR FILTERS (GLOBAL)
# =============================================================================
def sidebar_filters(df):
    st.sidebar.title("🔍 Filters")
    st.sidebar.markdown("---")
    
    # Year range
    years = sorted(df['year'].unique())
    year_range = st.sidebar.slider("Year Range", min_value=int(years[0]), max_value=int(years[-1]),
                                   value=(int(years[0]), int(years[-1])), step=1)
    
    # City multiselect
    cities = sorted(df['city'].dropna().unique())
    selected_cities = st.sidebar.multiselect("City", cities, default=cities[:5])
    
    # Sector multiselect
    sectors = sorted(df['vertical'].dropna().unique())
    selected_sectors = st.sidebar.multiselect("Sector", sectors, default=sectors[:5])
    
    # Stage multiselect
    stages = sorted(df['stage'].dropna().unique())
    selected_stages = st.sidebar.multiselect("Stage", stages, default=stages)
    
    return year_range, selected_cities, selected_sectors, selected_stages

# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    # Load data
    with st.spinner("Loading and preparing data..."):
        df, original = load_data()
    
    # Apply sidebar filters (global)
    year_range, selected_cities, selected_sectors, selected_stages = sidebar_filters(df)
    
    # Filter dataframe based on selections (for all dashboards)
    filtered_df = df[
        (df['year'] >= year_range[0]) & (df['year'] <= year_range[1]) &
        (df['city'].isin(selected_cities)) &
        (df['vertical'].isin(selected_sectors)) &
        (df['stage'].isin(selected_stages))
    ]
    
    # Navigation
    st.sidebar.markdown("---")
    st.sidebar.title("📂 Dashboards")
    app_mode = st.sidebar.radio("Select Dashboard", 
                                ["📊 Overall Analysis", "🚀 Startup Analysis", "💰 Investor Analysis"],
                                index=0)
    
    st.sidebar.markdown("---")
    st.sidebar.info("📅 Data updated: Latest available")
    st.sidebar.info("📌 Data source: Internal funding database")
    
    # Render selected dashboard
    if app_mode == "📊 Overall Analysis":
        overall_analysis(filtered_df, original)
    elif app_mode == "🚀 Startup Analysis":
        startup_analysis(filtered_df)
    elif app_mode == "💰 Investor Analysis":
        investor_analysis(filtered_df)

if __name__ == "__main__":
    main()
