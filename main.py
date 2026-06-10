# main.py
import pandas as pd
import folium
import plotly.express as px
from src.data_loader import load_and_preprocess_data, run_demand_forecasting
from src.optimizer import run_optimization_by_roi

# --- Configuration ---
DATA_PATH = "data/raw/capex_proposals.csv"
CAPEX_BUDGET_MILLION = 100.0  # R100 million budget cap

def generate_geospatial_map(df: pd.DataFrame):
    """Generates and saves an interactive Folium map to visuals/."""
    print("\n--- 🗺️ Generating Geospatial Map ---")
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
    
    map_path = "visuals/capex_recommendation_map.html"
    m.save(map_path)
    print(f"Interactive Map saved to: {map_path}")

def generate_analytical_chart(df: pd.DataFrame):
    """Generates and displays an interactive Plotly bar chart."""
    print("\n--- 📊 Generating Analytical Chart ---")
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
                 labels={'Avg_ROI': 'Average Projected ROI Ratio', 'Recommended_Count': 'Recommended Count'},
                 hover_data=['Total_CapEx', 'Recommended_Count'],
                 color_continuous_scale=px.colors.sequential.Viridis)

    chart_path = "visuals/roi_by_province_chart.html"
    fig.write_html(chart_path)
    print(f"Interactive Chart saved to: {chart_path}")
    print("\n--- PoC & Visualization Complete ---")


def main():
    """Coordinates the full CapEx optimization workflow."""
    
    print(f"🚀 Starting Advanced CapEx Optimization PoC | Budget: R{CAPEX_BUDGET_MILLION:,.0f}M\n")
    
    # 1. Load and Preprocess Data (includes feature engineering)
    df_raw = load_and_preprocess_data(DATA_PATH)
    if df_raw.empty: return

    # 2. Predictive Analytics (Demand Forecasting)
    df_forecasted = run_demand_forecasting(df_raw)

    # 3. CapEx Optimization
    df_final = run_optimization_by_roi(df_forecasted, CAPEX_BUDGET_MILLION)
    
    # 4. Results Presentation and Visualization
    
    # Summary of Recommended Projects
    optimized_projects = df_final[df_final['is_recommended_upgrade'] == True].head(5)
    print("\n✅ TOP 5 AI-RECOMMENDED UPGRADES:")
    print(optimized_projects[['tower_id', 'province', 'upgrade_cost_million_zar', 'projected_roi_ratio']].to_markdown(index=False, floatfmt=",.2f"))
    
    # Generate Visuals
    generate_geospatial_map(df_final)
    generate_analytical_chart(df_final)


if __name__ == "__main__":
    # Ensure the visuals folder exists before saving
    import os
    if not os.path.exists("visuals"):
        os.makedirs("visuals")
        
    main()