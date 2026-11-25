import pandas as pd
from modules.data_loader import detect_columns
from modules.preprocessing import clean_sales_data

def test_superstore_headers_are_detected_correctly():
    result=detect_columns(["Row ID","Order ID","Order Date","Ship Date","Sales","Product Name"])
    assert result["order_date"]=="Order Date"
    assert result["order_id"]=="Order ID"
    assert result["sales"]=="Sales"
    assert result["product"]=="Product Name"

def test_mapping_and_cleaning_works():
    raw=pd.DataFrame({"Order ID":["X1","X2"],"Order Date":["2024-01-01","2024-02-01"],
                      "Sales":["100","200"],"Product Name":["Pen","Book"]})
    mapping={"order_date":"Order Date","sales":"Sales","order_id":"Order ID","product":"Product Name"}
    clean,report=clean_sales_data(raw,mapping)
    assert "order_date" in clean.columns
    assert clean["sales"].sum()==300
    assert report["rows_prepared"]==2
