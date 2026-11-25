import pandas as pd
from modules.sales_analysis import calculate_kpis,monthly_revenue

def test_kpis():
    df=pd.DataFrame({"sales":[100,200],"order_id":["A","B"],"quantity":[1,2],"profit":[10,40]})
    k=calculate_kpis(df)
    assert k["total_revenue"]==300
    assert k["total_orders"]==2
    assert k["total_profit"]==50

def test_monthly_revenue():
    df=pd.DataFrame({"order_date":pd.to_datetime(["2024-01-01","2024-02-01"]),"sales":[100,200]})
    result=monthly_revenue(df)
    assert list(result["sales"])==[100,200]
