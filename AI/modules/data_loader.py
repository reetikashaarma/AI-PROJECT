from __future__ import annotations
from io import BytesIO
import pandas as pd
import re

ALIASES = {
    "order_date": ["order date", "order_date", "date", "transaction date", "sales date"],
    "sales": ["sales", "revenue", "amount", "total sales", "sales amount"],
    "order_id": ["order id", "order_id", "order number", "invoice", "invoice id"],
    "product": ["product name", "product", "item", "product_name"],
    "category": ["category", "product category"],
    "quantity": ["quantity", "qty", "units", "units sold"],
    "profit": ["profit", "net profit"],
    "region": ["region", "sales region", "territory"],
    "unit_price": ["unit price", "unit_price", "price per unit"],
    "cost_price": ["cost price", "cost_price", "unit cost"],
}

def normalize_name(value: object) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"[_\-]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text

def detect_columns(columns) -> dict:
    """Map standard internal fields to source column names using normalized exact aliases."""
    normalized = {normalize_name(col): col for col in columns}
    result = {}
    for field, aliases in ALIASES.items():
        match = next((normalized[a] for a in aliases if a in normalized), None)
        result[field] = match
    return result

def load_uploaded_file(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        frame = pd.read_csv(uploaded_file)
        return frame, "CSV"
    if name.endswith((".xlsx", ".xls")):
        book = pd.ExcelFile(uploaded_file)
        sheet = book.sheet_names[0]
        frame = pd.read_excel(book, sheet_name=sheet)
        return frame, sheet
    raise ValueError("Unsupported file. Upload CSV, XLSX or XLS.")

def load_file_path(path):
    path = str(path)
    if path.lower().endswith(".csv"):
        return pd.read_csv(path), "CSV"
    book = pd.ExcelFile(path)
    return pd.read_excel(book, sheet_name=book.sheet_names[0]), book.sheet_names[0]
