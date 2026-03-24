# agents/table_reasoning_agent.py

from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from memory.short_term import ShortTermMemory
from tools.table_tools import (
    list_to_dataframe,
    analyze_table,
    query_table,
    yoy_growth_table,
    top_n_rows,
    detect_anomalies,
)


class TableReasoningAgent(BaseAgent):
    """
    Analyzes financial tables from retrieved chunks.
    Converts raw data into DataFrames and runs analysis.
    """

    def __init__(self, memory: Optional[ShortTermMemory] = None):
        super().__init__(name="TableReasoningAgent", memory=memory)


    def run(self, query: str, context: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        context keys:
            table_data  — list of dicts  [{"year":"2024","revenue":81.4,...}]
            value_col   — column to analyze (default: "revenue")
            year_col    — year column name  (default: "year")
            sql         — optional SQL query to run on the table
        """
        try:
            table_data = context.get("table_data")
            if not table_data:
                return self.failure("No table_data provided in context.")

            value_col = context.get("value_col", "revenue")
            year_col  = context.get("year_col",  "year")
            sql       = context.get("sql")

            # build dataframe
            df = list_to_dataframe(table_data)

            results = {}

            # 1 — basic summary
            results["summary"] = analyze_table(df)

            # 2 — YoY growth if value + year columns exist
            if value_col in df.columns and year_col in df.columns:
                growth_df = yoy_growth_table(df.copy(), value_col, year_col)
                results["yoy_growth"] = growth_df.to_dict(orient="records")

            # 3 — top 3 rows by value column
            if value_col in df.columns:
                results["top_rows"] = top_n_rows(df, value_col, n=3).to_dict(orient="records")

            # 4 — anomaly detection
            if value_col in df.columns:
                anomaly_df = detect_anomalies(df.copy(), value_col)
                anomalies  = anomaly_df[anomaly_df[f"{value_col}_anomaly"] == True]
                results["anomalies"] = anomalies.to_dict(orient="records")

            # 5 — custom SQL query
            if sql:
                sql_result        = query_table(df, sql)
                results["sql_result"] = sql_result.to_dict(orient="records")

            self.remember("assistant", f"Table analysis complete: {list(results.keys())}")

            return self.success({
                "query"  : query,
                "results": results,
            })

        except Exception as e:
            return self.failure(str(e))


# --- Quick test ---
if __name__ == "__main__":
    agent = TableReasoningAgent()

    response = agent.run(
        query   = "Analyze Tesla revenue table",
        context = {
            "table_data": [
                {"year": "2022", "revenue": 70.0, "net_income": 8.0},
                {"year": "2023", "revenue": 75.0, "net_income": 9.0},
                {"year": "2024", "revenue": 81.4, "net_income": 10.2},
            ],
            "value_col": "revenue",
            "year_col" : "year",
            "sql"      : "SELECT year, revenue FROM df WHERE revenue > 72",
        }
    )

    print(f"Status : {response['status']}")
    print(f"\nSummary:\n{response['result']['results']['summary']}")
    print(f"\nYoY Growth:")
    for row in response["result"]["results"]["yoy_growth"]:
        print(f"  {row}")
    print(f"\nSQL Result:")
    for row in response["result"]["results"]["sql_result"]:
        print(f"  {row}")