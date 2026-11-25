import pandas as pd
from sklearn.ensemble import IsolationForest

def detect_revenue_anomalies(df, contamination=0.10):
    monthly = df.set_index("order_date")["sales"].resample("MS").sum().asfreq("MS", fill_value=0).rename("revenue").reset_index()
    monthly = monthly.rename(columns={"order_date":"month"})
    if len(monthly) < 8:
        return {"data":monthly.assign(is_anomaly=False, anomaly_score=0.0),
                "anomaly_count":0,"message":"At least 8 monthly observations are required."}
    monthly["monthly_change"] = monthly["revenue"].pct_change().replace([float("inf"),float("-inf")],0).fillna(0)
    features=monthly[["revenue","monthly_change"]].fillna(0)
    model=IsolationForest(n_estimators=200,contamination=float(contamination),random_state=42)
    monthly["is_anomaly"]=model.fit_predict(features)==-1
    monthly["anomaly_score"]=model.decision_function(features)
    return {"data":monthly,"anomaly_count":int(monthly["is_anomaly"].sum()),
            "message":"Flagged months are statistical outliers and should be investigated in context."}
