from __future__ import annotations
import pandas as pd

REQUIRED_FIELDS = ["order_date", "sales"]

def clean_sales_data(raw: pd.DataFrame, mapping: dict):
    """Rename mapped source columns to standard names and clean essential fields."""
    if raw is None or raw.empty:
        raise ValueError("The uploaded dataset is empty.")
    if not isinstance(mapping, dict):
        raise ValueError("Column mapping must be a dictionary.")

    selected = {}
    for field, source in mapping.items():
        if source is not None and source != "(Not available)":
            if source not in raw.columns:
                raise ValueError(f"Mapped source column '{source}' does not exist.")
            selected[field] = source

    missing = [field for field in REQUIRED_FIELDS if field not in selected]
    if missing:
        raise ValueError("Please map the required fields: " + ", ".join(missing))

    # Select only mapped columns, then rename to the application's standard schema.
    rename_map = {source: field for field, source in selected.items()}
    data = raw[list(dict.fromkeys(selected.values()))].copy()
    data = data.rename(columns=rename_map)

    report = {
        "rows_uploaded": int(len(data)),
        "invalid_dates_removed": 0,
        "invalid_sales_removed": 0,
        "duplicate_rows_removed": 0,
        "rows_prepared": 0,
    }

    data["order_date"] = pd.to_datetime(data["order_date"], errors="coerce")
    report["invalid_dates_removed"] = int(data["order_date"].isna().sum())
    data = data.dropna(subset=["order_date"]).copy()

    data["sales"] = pd.to_numeric(data["sales"], errors="coerce")
    report["invalid_sales_removed"] = int(data["sales"].isna().sum())
    data = data.dropna(subset=["sales"]).copy()

    for col in ["quantity", "profit", "unit_price", "cost_price"]:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    report["duplicate_rows_removed"] = int(data.duplicated().sum())
    data = data.drop_duplicates().copy()

    if "order_id" in data.columns:
        data["order_id"] = data["order_id"].astype("string")
    for col in ["product", "category", "region"]:
        if col in data.columns:
            data[col] = data[col].astype("string").fillna("Unknown")

    data["year"] = data["order_date"].dt.year
    data["month"] = data["order_date"].dt.to_period("M").astype(str)
    data["month_name"] = data["order_date"].dt.strftime("%b %Y")
    report["rows_prepared"] = int(len(data))
    if data.empty:
        raise ValueError("No valid rows remain after cleaning. Check the date and sales mappings.")
    return data.reset_index(drop=True), report
