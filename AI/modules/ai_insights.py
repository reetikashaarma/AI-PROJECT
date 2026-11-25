import pandas as pd

def generate_ai_insights(df):
    if df is None or df.empty:
        return {"summary":"No data is available.","insights":[],"recommendations":[]}
    data=df.copy()
    total=float(data.sales.sum())
    insights=[f"The selected dataset contains {len(data):,} rows and total revenue of {total:,.2f}."]
    recommendations=[]
    monthly=data.assign(period=data.order_date.dt.to_period("M")).groupby("period").sales.sum().sort_index()
    if len(monthly)>1:
        peak=monthly.idxmax()
        insights.append(f"Highest revenue month: {peak} ({monthly.max():,.2f}).")
        if len(monthly)>1 and monthly.iloc[-2]>0:
            change=(monthly.iloc[-1]-monthly.iloc[-2])/monthly.iloc[-2]*100
            insights.append(f"Latest month changed {change:+.1f}% compared with the previous month.")
            if change < -10:
                recommendations.append("Investigate the latest month's order volume, product mix, pricing and regional performance.")
            elif change > 10:
                recommendations.append("Identify which products and regions contributed to the recent increase.")
    if "product" in data.columns and data["product"].notna().any():
        p=data.groupby("product").sales.sum().sort_values(ascending=False)
        insights.append(f"Top product by revenue: {p.index[0]} ({p.iloc[0]:,.2f}).")
        if len(p)>1:
            recommendations.append(f"Review demand and pricing for the lowest-revenue product, {p.index[-1]}.")
    if "category" in data and data.category.notna().any():
        c=data.groupby("category").sales.sum().sort_values(ascending=False)
        insights.append(f"Leading category: {c.index[0]}.")
    if "region" in data and data.region.notna().any():
        r=data.groupby("region").sales.sum().sort_values(ascending=False)
        if len(r)>1: insights.append(f"Highest-revenue region: {r.index[0]}; lowest: {r.index[-1]}.")
    if "profit" in data:
        losses=int((pd.to_numeric(data.profit,errors="coerce")<0).sum())
        insights.append(f"{losses:,} rows have negative profit.")
        if losses: recommendations.append("Inspect loss-making transactions for discounting, shipping costs and product costs.")
    if not recommendations:
        recommendations.append("Continue monitoring monthly revenue and compare product, category and regional performance.")
    return {"summary":f"Analysis of {len(data):,} valid rows across {len(monthly):,} observed months.",
            "insights":insights,"recommendations":recommendations}
