# src/optimizer.py
import pandas as pd

def run_optimization_by_roi(df: pd.DataFrame, budget_cap: float) -> tuple[pd.DataFrame, float, float]:
    """
    Applies a greedy optimization strategy: rank by ROI and select projects 
    until the total cost exceeds the budget cap.
    
    Returns:
        pd.DataFrame: The original DataFrame with an added 'is_recommended_upgrade' column.
        float: total_investment (R Million)
        float: total_projected_revenue_gain (R Million)
    """
    print(f"\n--- 💰 Running CapEx Optimization Strategy for R{budget_cap:,.2f}M ---")
    
    # 1. Sort by ROI: The greedy approach (highest ROI first)
    ranked_data = df.sort_values(by='projected_roi_ratio', ascending=False)
    
    # 2. Apply Budget Constraint
    ranked_data['cumulative_cost'] = ranked_data['upgrade_cost_million_zar'].cumsum()
    ranked_data['is_recommended_upgrade'] = ranked_data['cumulative_cost'] <= budget_cap
    
    # 3. Calculate Summary KPIs
    optimized_portfolio = ranked_data[ranked_data['is_recommended_upgrade']].copy()
    
    total_investment = optimized_portfolio['upgrade_cost_million_zar'].sum()
    total_projected_revenue_gain = optimized_portfolio['annual_revenue_gain_million_zar'].sum()
    
    # Print summary to the console (for general logging)
    print(f"Total Invested: R{total_investment:,.2f} Million")
    print(f"Total Projected Annual Revenue Gain: R{total_projected_revenue_gain:,.2f} Million")
    print(f"Number of Recommended Upgrades: {optimized_portfolio.shape[0]}")

    # 4. RETURN the results, including the KPIs, for the dashboard
    return ranked_data.reset_index(), total_investment, total_projected_revenue_gain