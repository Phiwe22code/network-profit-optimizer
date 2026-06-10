# dashboard.py
import streamlit as st
import pandas as pd
import folium
import plotly.express as px
from streamlit_folium import folium_static
from src.data_loader import load_and_preprocess_data, run_demand_forecasting
from src.optimizer import run_optimization_by_roi

# --- Configuration ---
DATA_PATH = "data/raw/capex_proposals.csv"
MIN_BUDGET = 20.0
MAX_BUDGET = 100.0
DEFAULT_BUDGET = 50.0

# --- Dashboard Component Functions ---

def create_geospatial_map(df: pd.DataFrame):
    """Generates an interactive Folium map for Streamlit."""
    map_center = [-28.0, 24.0] # Center of South Africa
    m = folium.Map(location=map_center, zoom_start=5, tiles="cartodbpositron")

    for index, row in df.iterrows():
        color = 'green' if row['is_recommended_upgrade'] else 'red'
        popup_html = f"""
        <b>Tower ID:</b> {row['tower_id']}<br>
        <b>Province:</b> {row['province']}<br>
        <b>Upgrade Cost:</b> R{row['upgrade_cost_million_zar']:,.2f}M<br>
        <b>Projected ROI:</b> {row['projected_roi_ratio']:.2f}<br>
        <b>Recommendation:</b> {'YES' if row['is_recommended_upgrade'] else 'NO'}
        """
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=row['projected_roi_ratio'] * 5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(m)
    return m

def create_roi_chart(df: pd.DataFrame):
    """Generates an interactive Plotly bar chart for Streamlit."""
    province_summary = df.groupby('province').agg(
        Avg_ROI=('projected_roi_ratio', 'mean'),
        Total_CapEx=('upgrade_cost_million_zar', 'sum'),
        Recommended_Count=('is_recommended_upgrade', 'sum')
    ).reset_index()

    fig = px.bar(province_summary.sort_values(by='Avg_ROI', ascending=False),
                 x='province',
                 y='Avg_ROI',
                 color='Recommended_Count',
                 title='Average Projected ROI & Recommended Upgrades by Province',
                 labels={'Avg_ROI': 'Avg. Projected ROI Ratio', 'Recommended_Count': 'Recommended Count'},
                 hover_data=['Total_CapEx', 'Recommended_Count'],
                 color_continuous_scale=px.colors.sequential.Viridis)
    return fig

# --- Main Dashboard Function ---

def main_dashboard():
    st.set_page_config(layout="wide")
    st.title("📶 AI-Driven CapEx Optimization Dashboard")
    st.markdown("Execute scenario analysis based on predictive demand forecasting and budget constraints.")

    # 1. Load Data (Cache to prevent re-loading on every interaction)
    @st.cache_data
    def load_data():
        df_raw = load_and_preprocess_data(DATA_PATH)
        df_forecasted = run_demand_forecasting(df_raw)
        return df_forecasted

    df_initial = load_data()

    # --- Scenario Analysis Sidebar ---
    st.sidebar.header("🎯 Scenario Analysis")
    
    # Budget Slider (Scenario Input)
    budget_cap = st.sidebar.slider(
        "Select CapEx Budget (Million ZAR):",
        min_value=MIN_BUDGET,
        max_value=MAX_BUDGET,
        value=DEFAULT_BUDGET,
        step=5.0
    )
    
    st.sidebar.markdown(f"***Running optimization for R{budget_cap:,.2f} Million***")
    
    # 2. Run Optimization with Scenario Budget
    df_optimized, total_invest, total_revenue = run_optimization_by_roi(df_initial.copy(), budget_cap)
    
    # --- Display KPIs ---
    
    st.subheader("Financial Performance Summary")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("CapEx Budget", f"R{budget_cap:,.0f}M")
    col2.metric("Total Invested", f"R{total_invest:,.2f}M")
    col3.metric("Projected Annual Revenue Gain", f"R{total_revenue:,.2f}M")
    col4.metric("Total Towers Upgraded", f"{df_optimized['is_recommended_upgrade'].sum()}")

    st.markdown("---")
    
    # --- Display Visualizations (Visualization Section) ---
    
    st.subheader("Interactive Analysis")
    
    tab1, tab2 = st.tabs(["Geospatial Recommendation Map", "ROI Analysis Chart"])
    
    with tab1:
        st.markdown("Recommended towers are marked in **Green** and sized by **Projected ROI**.")
        map_obj = create_geospatial_map(df_optimized)
        folium_static(map_obj, width=1200, height=500)
    
    with tab2:
        chart_obj = create_roi_chart(df_optimized)
        st.plotly_chart(chart_obj, use_container_width=True)

    # --- Display Data Table ---
    
    st.subheader("Recommended Project List")
    st.dataframe(
        df_optimized[df_optimized['is_recommended_upgrade'] == True].sort_values(by='projected_roi_ratio', ascending=False),
        column_order=['tower_id', 'province', 'upgrade_cost_million_zar', 'annual_revenue_gain_million_zar', 'projected_roi_ratio'],
        hide_index=True
    )

if __name__ == "__main__":
    main_dashboard()