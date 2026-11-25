# AI-Powered Sales Analytics and Revenue Forecasting System

A Streamlit dashboard for sales data cleaning, business analytics, revenue forecasting, anomaly detection, insights and report exports.

## Features
- CSV, XLSX and XLS upload
- Automatic and manual column mapping
- Data cleaning and quality summary
- Revenue, orders, units, profit, AOV and margin KPIs
- Monthly revenue and growth analysis
- Product, category and regional performance
- Descriptive statistics and correlations
- Holt / Holt-Winters revenue forecasting
- Isolation Forest anomaly detection
- Local rule-based business insights
- PDF, Excel and CSV exports
- Project health checks

## Requirements
Python 3.10+ recommended. Windows and VS Code instructions:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

Run tests:
```powershell
python -m pytest -q
```

## Required dataset fields
At minimum, map:
- Order Date -> order_date
- Sales -> sales

Optional columns: Order ID, Product Name, Category, Quantity, Profit, Region, Unit Price, Cost Price.

## Important notes
- The insight engine is rule-based, not a hosted LLM.
- Forecasts are estimates, not guarantees. Seasonal forecasting needs at least 24 monthly observations.
- Missing months in forecasting are filled with zero revenue; verify this assumption for your data.
- Anomaly flags identify unusual patterns, not proof of fraud.
- Do not commit private datasets or credentials to GitHub.

## Project structure
See the modules/ directory for each component and tests/ for automated tests.
