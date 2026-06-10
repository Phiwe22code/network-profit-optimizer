# src/data_loader.py
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

def load_and_preprocess_data(file_path: str) -> pd.DataFrame:
    """
    Loads raw project data, performs feature engineering, and calculates initial metrics.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: Data file not found at {file_path}")
        return pd.DataFrame()

    # Convert Cost column to float
    df['upgrade_cost_million_zar'] = df['upgrade_cost_million_zar'].astype(float)
    
    # 1. Feature Engineering (Proxy for Future Demand/Revenue)
    # This formula is derived directly from the original Colab notebook logic
    df['potential_demand_index'] = (
        df['current_traffic_gb'] * df['population_density_ppkm'] * df['household_income_index']
    ) / 1e5
    
    # Simulated true future demand (Target for ML model)
    np.random.seed(42)
    noise = np.random.normal(0, 150, len(df))
    df['simulated_future_traffic_gb'] = (df['potential_demand_index'] * 50) + df['current_traffic_gb'] + noise

    print(f"Loaded and pre-processed {len(df)} tower proposals.")
    return df

def run_demand_forecasting(df: pd.DataFrame) -> pd.DataFrame:
    """
    Runs a Linear Regression model to predict future traffic (demand).
    """
    print("\n--- 🧠 Running Predictive Analytics (Demand Forecasting) ---")

    features = ['current_traffic_gb', 'population_density_ppkm', 'household_income_index', 'competitor_coverage_score']
    X = df[features]
    y = df['simulated_future_traffic_gb']

    # Split and Train Model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Predict on entire dataset
    df['ml_demand_forecast_gb'] = model.predict(X)
    
    # Calculate revenue and ROI based on ML forecast
    df['annual_revenue_gain_million_zar'] = df['ml_demand_forecast_gb'] * 0.0012 
    df['projected_roi_ratio'] = df['annual_revenue_gain_million_zar'] / df['upgrade_cost_million_zar']
    
    mse = mean_squared_error(y_test, model.predict(X_test))
    print(f"Model Trained: Linear Regression (MSE: {mse:,.2f})")
    
    return df.set_index('tower_id')