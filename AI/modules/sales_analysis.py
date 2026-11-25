import pandas as pd
import numpy as np

def calculate_kpis(df):
    revenue = float(df["sales"].sum()) if "sales" in df else 0.0
    orders = int(df["order_id"].nunique()) if "order_id" in df and df["order_id"].notna().any() else int(len(df))
    units = float(df["quantity"].sum()) if "quantity" in df and df["quantity"].notna().any() else None
    profit = float(df["profit"].sum()) if "profit" in df and df["profit"].notna().any() else None
    aov = revenue / orders if orders else 0.0
    margin = profit / revenue * 100 if profit is not None and revenue else None
    return {"total_revenue": revenue, "total_orders": orders, "units_sold": units,
            "total_profit": profit, "average_order_value": aov, "profit_margin_pct": margin}

def monthly_revenue(df):
    out = df.assign(month_period=df["order_date"].dt.to_period("M")).groupby("month_period", as_index=False)["sales"].sum()
    out["month"] = out["month_period"].astype(str)
    out = out.sort_values("month_period").reset_index(drop=True)
    out["mom_growth_pct"] = out["sales"].pct_change() * 100
    return out[["month", "sales", "mom_growth_pct"]]

def _group_performance(df, field):
    if field not in df.columns:
        return pd.DataFrame()
    result = df.groupby(field, dropna=False).agg(sales=("sales","sum")).reset_index()
    if "profit" in df.columns:
        prof = df.groupby(field, dropna=False)["profit"].sum().reset_index(name="profit")
        result = result.merge(prof, on=field, how="left")
    if "quantity" in df.columns:
        qty = df.groupby(field, dropna=False)["quantity"].sum().reset_index(name="quantity")
        result = result.merge(qty, on=field, how="left")
    total = result["sales"].sum()
    result["revenue_share_pct"] = result["sales"] / total * 100 if total else 0
    return result.sort_values("sales", ascending=False).reset_index(drop=True)

def product_performance(df): return _group_performance(df, "product")
def category_performance(df): return _group_performance(df, "category")
def regional_performance(df): return _group_performance(df, "region")

def descriptive_statistics(df):
    cols = [c for c in ["sales","quantity","profit"] if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    return df[cols].describe().T.reset_index(names="metric") if cols else pd.DataFrame()

def correlation_matrix(df):
    cols = [c for c in ["sales","quantity","profit"] if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
    return df[cols].corr(numeric_only=True) if len(cols) >= 2 else pd.DataFrame()

def generate_findings(df):
    if df.empty: return ["No data available."]
    findings=[]
    best_month=monthly_revenue(df)
    if not best_month.empty:
        peak=best_month.loc[best_month.sales.idxmax()]
        findings.append(f"Highest monthly revenue was {peak['month']} at {peak['sales']:,.2f}.")
    products=product_performance(df)
    if not products.empty:
        findings.append(f"Top product by revenue: {products.iloc[0]['product']} ({products.iloc[0]['sales']:,.2f}).")
    return findings
