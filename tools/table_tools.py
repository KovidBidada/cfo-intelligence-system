# tools/table_tools.py

import pandas as pd
import duckdb
from typing import Dict, Any, List


def list_to_dataframe(
    data   : List[Dict[str, Any]],
    columns: List[str] = None
) -> pd.DataFrame:
    """Convert list of dicts to DataFrame."""
    df = pd.DataFrame(data)
    if columns:
        df = df[columns]
    return df


def analyze_table(df: pd.DataFrame) -> Dict[str, Any]:
    """Basic statistical summary of a financial table."""
    numeric = df.select_dtypes(include="number")
    return {
        "rows"   : len(df),
        "columns": list(df.columns),
        "summary": numeric.describe().round(2).to_dict(),
    }


def query_table(df: pd.DataFrame, sql: str) -> pd.DataFrame:
    """
    Run SQL query on a DataFrame using DuckDB.
    Use 'df' as the table name in your SQL.

    Example:
        query_table(df, "SELECT year, revenue FROM df WHERE revenue > 75")
    """
    return duckdb.query(sql).df()


def yoy_growth_table(df: pd.DataFrame, value_col: str, year_col: str) -> pd.DataFrame:
    """Add YoY growth % column to a financial table."""
    df = df.sort_values(year_col).reset_index(drop=True)
    df[f"{value_col}_yoy_%"] = df[value_col].pct_change().mul(100).round(2)
    return df


def top_n_rows(df: pd.DataFrame, col: str, n: int = 3) -> pd.DataFrame:
    """Return top N rows by a column value."""
    return df.nlargest(n, col)


def detect_anomalies(df: pd.DataFrame, col: str, threshold: float = 2.0) -> pd.DataFrame:
    """Flag rows where value deviates beyond threshold standard deviations."""
    mean = df[col].mean()
    std  = df[col].std()
    df[f"{col}_anomaly"] = (df[col] - mean).abs() > (threshold * std)
    return df


# --- Quick test ---
if __name__ == "__main__":
    data = [
        {"year": "2022", "revenue": 70.0, "net_income": 8.0},
        {"year": "2023", "revenue": 75.0, "net_income": 9.0},
        {"year": "2024", "revenue": 81.4, "net_income": 10.2},
    ]

    df = list_to_dataframe(data)
    print("--- Table ---")
    print(df)

    print("\n--- Summary ---")
    print(analyze_table(df))

    print("\n--- SQL Query ---")
    result = query_table(df, "SELECT year, revenue FROM df WHERE revenue > 72")
    print(result)

    print("\n--- YoY Growth ---")
    print(yoy_growth_table(df, value_col="revenue", year_col="year"))

    print("\n--- Top 2 by Revenue ---")
    print(top_n_rows(df, col="revenue", n=2))

    print("\n--- Anomaly Detection ---")
    print(detect_anomalies(df, col="revenue"))