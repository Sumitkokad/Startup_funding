import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import re

# Page Configuration
st.set_page_config(
    page_title="Startup Funding Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .subheader {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin: 0;
    }
    .section-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 4px solid #1f77b4;
    }
    .download-btn {
        background: #28a745;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 5px;
        cursor: pointer;
        font-weight: 500;
    }
    .download-btn:hover {
        background: #218838;
    }
    @media (max-width: 768px) {
        .metric-card {
            margin-bottom: 15px;
        }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and preprocess the dataset"""
    # Load data
    df = pd.read_csv('startup_funding_clean.csv')
    original = pd.read_csv('df_original.csv')
    
    # Investors preprocessing
    df['investors'] = df['investors'].astype(str).str.replace(r'\\n|\n|\\x[a-fA-F0-9]{2}|\\', '', regex=True)
    
    # Round processing for stages
    df['round'] = df['round'].str.replace('\\\\n', '').str.replace('/', ',').str.lower()
    
    # Stage mapping
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
    
    # Startup and city processing
    df['startup'] = df['startup'].str.replace("BYJU's", "Byju's")
    df['city'] = df['city'].str.replace('Bangalore', 'Bengaluru')
    
    # Date processing
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['month_year'] = df['date'].dt.to_period('M').astype(str)
    
    return df, original

# Load data
df, original = load_data()

def create_kpi_card(title, value, subtitle=""):
    """Create a professional KPI card"""
    return f"""
    <div class="metric-card">
        <p class="metric-label">{title}</p>
        <h3 class="metric-value">{value}</h3>
        <p class="metric-label">{subtitle}</p>
    </div>
    """

def overall_analysis():
    """Overall Analysis Dashboard"""
    st.markdown('<div class="main-header">📊 Startup Funding Analytics Dashboard</div>', unsafe_allow_html=True)
    
    # Executive Summary KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_funding = round(original['amount'].sum(), 2)
        st.markdown(create_kpi_card("Total Funding", f"₹{total_funding:,.0f} Cr", "Cumulative Investment"), unsafe_allow_html=True)
    
    with col2:
        peak_funding = original['amount'].max()
        st.markdown(create_kpi_card("Peak Funding", f"₹{peak_funding:,.0f} Cr", "Largest Single Round"), unsafe_allow_html=True)
    
    with col3:
        avg_funding = round(original['amount'].mean(), 2)
        st.markdown(create_kpi_card("Average Funding", f"₹{avg_funding:,.0f} Cr", "Per Funding Round"), unsafe_allow_html=True)
    
    with col4:
        total_startups = df['startup'].nunique()
        st.markdown(create_kpi_card("Total Startups", f"{total_startups:,}", "Unique Companies"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Trends Section
    st.markdown('<div class="subheader">📈 Funding Trends</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly Trend
        monthly_trend = df.groupby('month_year')['amount'].sum().reset_index()
        fig = px.line(monthly_trend, x='month_year', y='amount', 
                     title="Monthly Funding Trend", markers=True)
        fig.update_layout(xaxis_title="Month", yaxis_title="Funding Amount (Cr)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Yearly Trend
        yearly_trend = df.groupby('year')['amount'].sum().reset_index()
        fig = px.bar(yearly_trend, x='year', y='amount', 
                    title="Yearly Funding Distribution", text_auto=True)
        fig.update_layout(xaxis_title="Year", yaxis_title="Funding Amount (Cr)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Funding Analysis Section
    st.markdown('<div class="subheader">💰 Funding Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Funding Type Distribution
        funding_type = df['round'].value_counts().head(10)
        fig = px.bar(x=funding_type.values, y=funding_type.index, orientation='h',
                    title="Top Funding Types", text_auto=True)
        fig.update_layout(xaxis_title="Count", yaxis_title="Funding Type")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Stage Distribution
        stage_dist = df['stage'].value_counts()
        fig = px.pie(values=stage_dist.values, names=stage_dist.index,
                    title="Funding Stage Distribution", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    # Geographic Analysis
    st.markdown('<div class="subheader">🌍 Geographic Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # City-wise Funding
        city_funding = df.groupby('city')['amount'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(x=city_funding.values, y=city_funding.index, orientation='h',
                    title="Top Cities by Funding", text_auto=True)
        fig.update_layout(xaxis_title="Funding Amount (Cr)", yaxis_title="City")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Funding Heatmap
        heatmap_data = df.pivot_table(index='city', columns='year', values='amount', aggfunc='sum').fillna(0)
        fig = px.imshow(heatmap_data, text_auto=True, aspect='auto',
                       title="City vs Year Funding Heatmap")
        st.plotly_chart(fig, use_container_width=True)
    
    # Leaderboards
    st.markdown('<div class="subheader">🏆 Leaderboards</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top Startups
        top_startups = df.groupby('startup')['amount'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(x=top_startups.values, y=top_startups.index, orientation='h',
                    title="Top 10 Startups by Funding", text_auto=True)
        fig.update_layout(xaxis_title="Funding Amount (Cr)", yaxis_title="Startup")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top Investors
        top_investors = df.groupby('investors')['amount'].sum().sort_values(ascending=False).head(10)
        fig = px.bar(x=top_investors.values, y=top_investors.index, orientation='h',
                    title="Top 10 Investors by Funding", text_auto=True)
        fig.update_layout(xaxis_title="Funding Amount (Cr)", yaxis_title="Investor")
        st.plotly_chart(fig, use_container_width=True)

def startup_analysis():
    """Startup Analysis Dashboard"""
    st.markdown('<div class="main-header">🚀 Startup Analysis</div>', unsafe_allow_html=True)
    
    # Startup selection
    startup_options = sorted(df['startup'].unique().tolist())
    selected_startup = st.selectbox("Select Startup", startup_options, key='startup_select')
    
    if selected_startup:
        startup_df = df[df['startup'] == selected_startup]
        
        # Startup Overview KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_funding = startup_df['amount'].sum()
            st.markdown(create_kpi_card("Total Funding", f"₹{total_funding:,.0f} Cr", "Cumulative"), unsafe_allow_html=True)
        
        with col2:
            funding_rounds = len(startup_df)
            st.markdown(create_kpi_card("Funding Rounds", f"{funding_rounds}", "Total Rounds"), unsafe_allow_html=True)
        
        with col3:
            latest_round = startup_df['date'].max().strftime('%b %Y')
            st.markdown(create_kpi_card("Latest Round", latest_round, "Most Recent"), unsafe_allow_html=True)
        
        with col4:
            top_investor = startup_df['investors'].value_counts().index[0] if not startup_df.empty else "N/A"
            st.markdown(create_kpi_card("Top Investor", top_investor[:20] + "..." if len(top_investor) > 20 else top_investor, "Most Active"), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Detailed Information
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Startup Details**")
            st.write(f"**Industry:** {startup_df['vertical'].iloc[0] if not startup_df.empty else 'N/A'}")
            st.write(f"**Subindustry:** {startup_df['subvertical'].iloc[0] if not startup_df.empty else 'N/A'}")
            st.write(f"**Location:** {startup_df['city'].iloc[0] if not startup_df.empty else 'N/A'}")
        
        with col2:
            st.markdown("**Funding Summary**")
            st.write(f"**First Funding:** {startup_df['date'].min().strftime('%b %Y') if not startup_df.empty else 'N/A'}")
            st.write(f"**Funding Stages:** {', '.join(startup_df['stage'].unique()) if not startup_df.empty else 'N/A'}")
            st.write(f"**Unique Investors:** {startup_df['investors'].nunique() if not startup_df.empty else 'N/A'}")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Funding Timeline
            timeline = startup_df.sort_values('date')
            fig = px.line(timeline, x='date', y='amount', markers=True,
                         title="Funding Timeline", labels={'amount': 'Funding Amount (Cr)'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Round Distribution
            round_dist = startup_df['round'].value_counts()
            fig = px.bar(x=round_dist.values, y=round_dist.index, orientation='h',
                        title="Funding Round Distribution", text_auto=True)
            st.plotly_chart(fig, use_container_width=True)
        
        # Investor Analysis
        st.markdown("**Investor Participation**")
        investor_data = startup_df['investors'].value_counts().reset_index()
        investor_data.columns = ['Investor', 'Count']
        st.dataframe(investor_data, use_container_width=True)
        
        # Download button
        if st.button("📥 Download Startup Report", key='startup_download'):
            # Create downloadable report
            csv = startup_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{selected_startup}_funding_report.csv",
                mime="text/csv"
            )

def investor_analysis():
    """Investor Analysis Dashboard"""
    st.markdown('<div class="main-header">💰 Investor Analysis</div>', unsafe_allow_html=True)
    
    # Investor selection
    investor_options = sorted(df['investors'].dropna().unique().tolist())
    selected_investor = st.selectbox("Select Investor", investor_options, key='investor_select')
    
    if selected_investor:
        investor_df = df[df['investors'].str.contains(selected_investor, na=False, regex=False)]
        
        # Investor Overview KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_investments = len(investor_df)
            st.markdown(create_kpi_card("Total Investments", f"{total_investments}", "Portfolio Size"), unsafe_allow_html=True)
        
        with col2:
            total_funding = investor_df['amount'].sum()
            st.markdown(create_kpi_card("Total Funding", f"₹{total_funding:,.0f} Cr", "Investment Value"), unsafe_allow_html=True)
        
        with col3:
            avg_investment = investor_df['amount'].mean()
            st.markdown(create_kpi_card("Avg Investment", f"₹{avg_investment:,.0f} Cr", "Per Deal"), unsafe_allow_html=True)
        
        with col4:
            portfolio_companies = investor_df['startup'].nunique()
            st.markdown(create_kpi_card("Portfolio Companies", f"{portfolio_companies}", "Unique Startups"), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Investment Analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Sector Allocation
            sector_allocation = investor_df['vertical'].value_counts().head(8)
            fig = px.pie(values=sector_allocation.values, names=sector_allocation.index,
                        title="Sector Allocation", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Stage Allocation
            stage_allocation = investor_df['stage'].value_counts()
            fig = px.bar(x=stage_allocation.values, y=stage_allocation.index, orientation='h',
                        title="Stage Allocation", text_auto=True)
            st.plotly_chart(fig, use_container_width=True)
        
        # Geographic Analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # City Allocation
            city_allocation = investor_df['city'].value_counts().head(8)
            fig = px.bar(x=city_allocation.values, y=city_allocation.index, orientation='h',
                        title="City Allocation", text_auto=True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Investment Timeline
            yearly_investment = investor_df.groupby('year')['amount'].sum().reset_index()
            fig = px.line(yearly_investment, x='year', y='amount', markers=True,
                         title="Yearly Investment Trend", labels={'amount': 'Funding Amount (Cr)'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Top Investments
        st.markdown("**Top 5 Investments**")
        top_investments = investor_df.nlargest(5, 'amount')[['startup', 'amount', 'round', 'date']]
        top_investments['date'] = top_investments['date'].dt.strftime('%Y-%m-%d')
        st.dataframe(top_investments, use_container_width=True)
        
        # Recent Investments
        st.markdown("**Recent Investments**")
        recent_investments = investor_df.nlargest(10, 'date')[['startup', 'amount', 'round', 'date', 'vertical']]
        recent_investments['date'] = recent_investments['date'].dt.strftime('%Y-%m-%d')
        st.dataframe(recent_investments, use_container_width=True)
        
        # Download button
        if st.button("📥 Download Investor Report", key='investor_download'):
            csv = investor_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{selected_investor}_portfolio_report.csv",
                mime="text/csv"
            )

# Sidebar Navigation
st.sidebar.title("📊 Navigation")
app_mode = st.sidebar.radio("Select Dashboard", 
                           ["Overall Analysis", "Startup Analysis", "Investor Analysis"])

# Main app logic
if app_mode == "Overall Analysis":
    overall_analysis()
elif app_mode == "Startup Analysis":
    startup_analysis()
elif app_mode == "Investor Analysis":
    investor_analysis()

# Footer
st.sidebar.markdown("---")
st.sidebar.info("📅 Data updated: Latest available")
st.sidebar.info("🔒 Data Source: Internal funding database")
