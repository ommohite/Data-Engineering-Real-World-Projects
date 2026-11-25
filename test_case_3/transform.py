"""Clean sales transactions and prepare calendar reporting columns."""

import pandas as pd

REQUIRED_COLUMNS = [
    "sale_id", "order_id", "customer_id", "product_id", "sale_date",
    "quantity", "unit_price", "total_amount",
]


def data_transformation(source: pd.DataFrame) -> pd.DataFrame:
    """Clean sales rows and derive year, month, month name, and quarter."""
    missing = set(REQUIRED_COLUMNS) - set(source.columns)
    if missing:
        raise ValueError(f"sales_source is missing required columns: {sorted(missing)}")

    df = source.copy().drop_duplicates().reset_index(drop=True)
    for key in ("sale_id", "order_id", "customer_id", "product_id"):
        df = df.loc[df[key].notna()].copy()

    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
    df.loc[df["quantity"] <= 0, "quantity"] = 1

    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    positive_prices = df.loc[df["unit_price"] > 0, "unit_price"]
    if positive_prices.empty:
        raise ValueError("Cannot impute unit_price: no positive price values found.")
    average_price = positive_prices.mean()
    df["unit_price"] = df["unit_price"].fillna(average_price)
    df.loc[df["unit_price"] <= 0, "unit_price"] = average_price

    calculated_amount = df["unit_price"] * df["quantity"]
    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce")
    df["total_amount"] = df["total_amount"].fillna(calculated_amount)

    df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
    if df["sale_date"].isna().any():
        raise ValueError("Invalid or missing sale_date values remain after extraction.")
    df["year"] = df["sale_date"].dt.year
    df["month"] = df["sale_date"].dt.month
    df["month_name"] = df["sale_date"].dt.month_name()
    df["quarter"] = df["sale_date"].dt.quarter
    return df.reset_index(drop=True)


def build_sales_reports(df: pd.DataFrame, report_year: int = 2025) -> dict[str, pd.Series]:
    """Build all-years, requested-year monthly, and requested-year quarterly totals."""
    year_rows = df.loc[df["year"] == report_year]
    return {
        "yearly_report": df.groupby("year")["total_amount"].sum().sort_index(),
        "monthly_report": year_rows.groupby("month")["total_amount"].sum().reindex(range(1, 13), fill_value=0),
        "quarterly_report": year_rows.groupby("quarter")["total_amount"].sum().reindex(range(1, 5), fill_value=0),
    }
