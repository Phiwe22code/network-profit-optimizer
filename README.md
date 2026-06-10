# Telkom CapEx Optimization

An AI-assisted capital expenditure planning tool for telecom tower upgrades. Combines a machine learning demand forecast with a greedy ROI-based optimizer to help prioritize upgrade projects under a fixed budget.

> **Context:** Built as part of the SATNAC 2025 Industry Solutions Challenge — awarded 1st place in the competition.

---

## Overview

Given a list of proposed tower upgrades, this tool answers: **which projects should be funded first to maximize projected annual revenue gain while staying within budget?**

The pipeline:
1. Loads and preprocesses raw tower proposal data
2. Engineers a demand proxy from traffic and market signals
3. Trains a linear regression model to forecast future traffic
4. Converts the forecast into projected revenue and ROI
5. Selects the highest-ROI upgrades until the budget cap is reached

---

## Project Structure

```
Telkom CapEx/
├── main.py                        # CLI entry point — runs full pipeline
├── dashboard.py                   # Streamlit dashboard for interactive analysis
├── requirements.txt
├── README.md
├── data/
│   └── raw/
│       └── capex_proposals.csv    # Input dataset
├── models/
├── notebooks/
├── src/
│   ├── __init__.py
│   ├── data_loader.py             # Preprocessing, feature engineering, model training
│   └── optimizer.py               # ROI ranking and budget-constrained selection
└── visuals/                       # Output HTML artifacts
```

---

## Dataset

**File:** `data/raw/capex_proposals.csv`

Each row represents one tower upgrade proposal.

| Column | Description |
|---|---|
| `tower_id` | Unique tower identifier |
| `province` | Province name |
| `lat`, `lon` | Geographic coordinates |
| `current_traffic_gb` | Current traffic volume (GB) |
| `population_density_ppkm` | Population density per km² |
| `household_income_index` | Normalized household income proxy |
| `competitor_coverage_score` | Competitor presence/coverage pressure |
| `upgrade_cost_million_zar` | Upgrade cost (million ZAR) |

The pipeline also derives: `potential_demand_index`, `ml_demand_forecast_gb`, `annual_revenue_gain_million_zar`, `projected_roi_ratio`, `cumulative_cost`, and `is_recommended_upgrade`.

---

## Methodology

### 1. Preprocessing (`src/data_loader.py`)
Reads the CSV, coerces numeric types, and creates a demand proxy from traffic volume, population density, and household income.

### 2. Demand Forecasting
A `LinearRegression` model trained on `current_traffic_gb`, `population_density_ppkm`, `household_income_index`, and `competitor_coverage_score` predicts future traffic per tower. This is converted to:
- `annual_revenue_gain_million_zar` via a fixed revenue factor
- `projected_roi_ratio` = revenue gain / upgrade cost

### 3. Optimization (`src/optimizer.py`)
A greedy algorithm sorts proposals by `projected_roi_ratio` descending, tracks cumulative spend, and marks towers as recommended while spend remains within the budget cap.

> Note: This is a greedy approach — it is fast and interpretable but does not guarantee a mathematically optimal portfolio in all cases. A `pulp` dependency is included in `requirements.txt` for a future ILP upgrade.

---

## Outputs

| Artifact | Description |
|---|---|
| `visuals/capex_recommendation_map.html` | Interactive Folium map — tower locations, recommendation status, ROI-scaled markers |
| `visuals/roi_by_province_chart.html` | Interactive Plotly chart — average ROI and recommendation counts by province |

Map markers: **green** = recommended, **red** = not recommended. Marker size scales with `projected_roi_ratio`.

---

## Setup

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
pip install streamlit-folium
```

> `streamlit-folium` is required by the dashboard but is not yet in `requirements.txt`.

### 3. Verify the data file

Confirm that `data/raw/capex_proposals.csv` exists and contains the expected columns listed above.

---

## Usage

### Command-line pipeline

```powershell
python main.py
```

Runs the full workflow and saves HTML outputs to `visuals/`.

> **Known issue:** `main.py` expects `run_optimization_by_roi()` to return a DataFrame, but the function returns a tuple `(df, total_investment, total_projected_revenue_gain)`. Unpack accordingly before the final summary and visualization steps.

### Streamlit dashboard

```powershell
streamlit run dashboard.py
```

The dashboard provides:
- Budget slider (R20M – R100M, default R50M)
- KPI cards: budget, investment, projected revenue gain, number of upgraded towers
- Interactive Folium map
- Plotly ROI chart by province
- Ranked table of recommended projects

---

## Requirements

```
pandas
numpy
scikit-learn
plotly
folium
pulp
streamlit
streamlit-folium  # dashboard only — install separately
```

---

## Limitations

- The model trains on a **simulated** future-traffic target — results are illustrative, not financially authoritative.
- The revenue conversion factor is hard-coded in `src/data_loader.py`.
- The optimizer is greedy; `pulp` is present but not yet wired up.
- `requirements.txt` does not include `streamlit-folium`.

---

## Roadmap

-  Replace simulated target with historical demand or revenue data
-  Upgrade optimizer from greedy selection to integer linear programming (ILP) via `pulp`
-  Move hard-coded assumptions (revenue factor, budget bounds) to a config file
-  Add `streamlit-folium` to `requirements.txt`
-  Add unit tests for data loading, forecasting, and optimization steps

---

## Troubleshooting

**Data file not found** — run commands from the project root directory.

**Missing module error in Streamlit** — run `pip install streamlit-folium`.

**`main.py` crashes at optimization step** — unpack the tuple returned by `run_optimization_by_roi()`:
```python
df, total_investment, total_revenue = run_optimization_by_roi(df, budget=100.0)
```
