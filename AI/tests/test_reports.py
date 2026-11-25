import pandas as pd
from modules.report_generator import build_excel_report,build_pdf_report

def test_excel_and_pdf_creation():
    k={"total_revenue":100.0,"total_orders":1}
    m=pd.DataFrame({"month":["2024-01"],"sales":[100]})
    empty=pd.DataFrame()
    x=build_excel_report(pd.DataFrame({"sales":[100]}),k,m,empty,empty,empty)
    p=build_pdf_report(k,m,empty,empty,empty)
    assert x[:2]==b"PK"
    assert p.startswith(b"%PDF")
