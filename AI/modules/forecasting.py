import pandas as pd
import numpy as np

def monthly_series(df):
    series = df.set_index("order_date")["sales"].resample("MS").sum().asfreq("MS", fill_value=0.0)
    return series.astype(float)

def forecast_revenue(df, horizon=3):
    from statsmodels.tsa.holtwinters import ExponentialSmoothing, Holt
    series = monthly_series(df)
    if len(series) < 3:
        raise ValueError("At least 3 monthly observations are required for forecasting.")
    if horizon not in (3,6,12):
        raise ValueError("Forecast horizon must be 3, 6 or 12 months.")
    seasonal = len(series) >= 24
    try:
        if seasonal:
            model = ExponentialSmoothing(series, trend="add", seasonal="add", seasonal_periods=12,
                                         initialization_method="estimated").fit(optimized=True)
            name="Holt-Winters additive seasonal"
        else:
            model = Holt(series, initialization_method="estimated").fit(optimized=True)
            name="Holt linear trend"
        values = np.maximum(model.forecast(horizon).to_numpy(), 0)
    except Exception as exc:
        raise ValueError(f"Forecast could not be calculated for this dataset: {exc}")
    future_dates = pd.date_range(series.index[-1] + pd.offsets.MonthBegin(1), periods=horizon, freq="MS")
    forecast = pd.DataFrame({"month": future_dates.strftime("%Y-%m"), "predicted_revenue": values})
    fitted = model.fittedvalues
    mae = float(np.mean(np.abs(series.iloc[1:].to_numpy()-fitted.iloc[1:].to_numpy())))
    rmse = float(np.sqrt(np.mean((series.iloc[1:].to_numpy()-fitted.iloc[1:].to_numpy())**2)))
    history = pd.DataFrame({"month":series.index.strftime("%Y-%m"),"actual_revenue":series.values})
    return {"history":history,"forecast":forecast,"model_name":name,"seasonality_used":seasonal,
            "observations":len(series),"evaluation":{"mae":mae,"rmse":rmse,
            "message":"In-sample error metrics; use them as indicative diagnostics, not a guarantee of future accuracy."}}
