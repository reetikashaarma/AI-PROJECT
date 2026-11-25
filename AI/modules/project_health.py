from pathlib import Path
import importlib.util, platform

PACKAGES=["streamlit","pandas","numpy","plotly","openpyxl","sklearn","statsmodels","reportlab"]
PROJECT_FILES=["app.py","requirements.txt","modules/data_loader.py","modules/preprocessing.py",
"modules/sales_analysis.py","modules/forecasting.py","modules/anomaly_detection.py",
"modules/ai_insights.py","modules/report_generator.py"]
def build_health_report(root=".",df=None):
    root=Path(root).resolve()
    checks=[]
    for name in PACKAGES:
        ok=importlib.util.find_spec(name) is not None
        checks.append({"check":f"Package: {name}","status":"Ready" if ok else "Missing"})
    for name in PROJECT_FILES:
        ok=(root/name).is_file()
        checks.append({"check":f"File: {name}","status":"Ready" if ok else "Missing"})
    if df is not None:
        for col in ["order_date","sales"]:
            ok=col in df.columns
            checks.append({"check":f"Dataset: {col}","status":"Ready" if ok else "Missing"})
    missing=sum(x["status"]=="Missing" for x in checks)
    return {"python_version":platform.python_version(),"checks":checks,
            "ready_count":len(checks)-missing,"missing_count":missing,
            "overall_status":"Ready" if missing==0 else "Needs attention"}
