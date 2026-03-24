# agents/financial_analyst_agent.py

from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from memory.short_term import ShortTermMemory
from tools.financial_ratios import (
    profit_margin,
    gross_margin,
    operating_margin,
    debt_to_equity,
    current_ratio,
    return_on_equity,
)
from tools.growth_calculator import yoy_growth, cagr
from tools.cash_flow_tools import free_cash_flow, cash_flow_margin


class FinancialAnalystAgent(BaseAgent):
    """
    Computes financial ratios, growth metrics,
    and generates insights from extracted KPIs.
    """

    def __init__(self, memory: Optional[ShortTermMemory] = None):
        super().__init__(name="FinancialAnalystAgent", memory=memory)


    def run(self, query: str, context: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        context keys (from KPIExtractionAgent):
            kpis        — dict of extracted KPIs
            prev_kpis   — dict of previous year KPIs (optional)
        """
        try:
            kpis      = context.get("kpis", {})
            prev_kpis = context.get("prev_kpis", {})

            if not kpis:
                return self.failure("No KPIs provided in context.")

            analysis = {}

            # --- Margin Analysis ---
            if "revenue" in kpis and "net_income" in kpis:
                analysis["profit_margin"] = profit_margin(
                    kpis["revenue"], kpis["net_income"]
                )

            if "revenue" in kpis and "gross_profit" in kpis:
                cogs = kpis["revenue"] - kpis["gross_profit"]
                analysis["gross_margin"] = gross_margin(
                    kpis["revenue"], cogs
                )

            if "revenue" in kpis and "operating_income" in kpis:
                analysis["operating_margin"] = operating_margin(
                    kpis["revenue"], kpis["operating_income"]
                )

            # --- Liquidity & Leverage ---
            if "total_debt" in kpis and "total_equity" in kpis:
                analysis["debt_to_equity"] = debt_to_equity(
                    kpis["total_debt"], kpis["total_equity"]
                )

            if "current_assets" in kpis and "current_liabilities" in kpis:
                analysis["current_ratio"] = current_ratio(
                    kpis["current_assets"], kpis["current_liabilities"]
                )

            if "net_income" in kpis and "total_equity" in kpis:
                analysis["return_on_equity"] = return_on_equity(
                    kpis["net_income"], kpis["total_equity"]
                )

            # --- Cash Flow ---
            if "cash_flow" in kpis and "capex" in kpis:
                analysis["free_cash_flow"] = free_cash_flow(
                    kpis["cash_flow"], kpis["capex"]
                )

            if "cash_flow" in kpis and "revenue" in kpis:
                analysis["cash_flow_margin"] = cash_flow_margin(
                    kpis["cash_flow"], kpis["revenue"]
                )

            # --- YoY Growth (if prev_kpis provided) ---
            if prev_kpis:
                growth = {}
                for metric in ["revenue", "net_income", "operating_income"]:
                    if metric in kpis and metric in prev_kpis:
                        growth[metric] = yoy_growth(
                            kpis[metric], prev_kpis[metric]
                        )
                if growth:
                    analysis["yoy_growth"] = growth

            # --- Risk Flags ---
            risks = []
            if "debt_to_equity" in analysis:
                if analysis["debt_to_equity"]["ratio"] > 2:
                    risks.append("High debt-to-equity ratio")
            if "current_ratio" in analysis:
                if analysis["current_ratio"]["ratio"] < 1:
                    risks.append("Current ratio below 1 — liquidity risk")
            if "profit_margin" in analysis:
                if analysis["profit_margin"]["margin_%"] < 5:
                    risks.append("Low profit margin below 5%")

            analysis["risk_flags"] = risks

            self.remember("assistant", f"Analysis done: {list(analysis.keys())}")

            return self.success({
                "query"   : query,
                "analysis": analysis,
            })

        except Exception as e:
            return self.failure(str(e))


# --- Quick test ---
if __name__ == "__main__":
    agent = FinancialAnalystAgent()

    response = agent.run(
        query   = "Analyze Tesla 2024 financials",
        context = {
            "kpis": {
                "revenue"          : 81.4,
                "net_income"       : 10.2,
                "gross_profit"     : 17.5,
                "operating_income" : 13.7,
                "cash_flow"        : 14.9,
                "capex"            : 8.9,
                "total_debt"       : 5.0,
                "total_equity"     : 20.0,
                "current_assets"   : 30.0,
                "current_liabilities": 10.0,
            },
            "prev_kpis": {
                "revenue"          : 75.0,
                "net_income"       : 9.0,
                "operating_income" : 12.0,
            }
        }
    )

    print(f"Status: {response['status']}")
    for k, v in response["result"]["analysis"].items():
        print(f"\n{k}:\n  {v}")