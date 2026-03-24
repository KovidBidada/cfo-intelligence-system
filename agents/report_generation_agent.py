# agents/report_generation_agent.py

from typing import Dict, Any, Optional
from datetime import datetime
from agents.base_agent import BaseAgent
from memory.short_term import ShortTermMemory


class ReportGenerationAgent(BaseAgent):
    """
    Generates a professional CFO financial report
    from analysis, KPIs, and table results.
    """

    def __init__(self, memory: Optional[ShortTermMemory] = None):
        super().__init__(name="ReportGenerationAgent", memory=memory)


    def _format_kpis(self, kpis: Dict) -> str:
        lines = []
        for k, v in kpis.items():
            lines.append(f"  - {k.replace('_', ' ').title()}: {v}")
        return "\n".join(lines)


    def _format_analysis(self, analysis: Dict) -> str:
        lines = []
        for key, val in analysis.items():
            if key == "risk_flags":
                continue
            if isinstance(val, dict):
                metric  = val.get("metric", key)
                insight = val.get("insight", "")
                # pick first numeric value
                numeric = next(
                    (f"{v}" for k, v in val.items()
                     if isinstance(v, float) and k != "score"),
                    ""
                )
                lines.append(f"  - {metric.replace('_',' ').title()}: {numeric}  {insight}")
        return "\n".join(lines)


    def _format_growth(self, growth: Dict) -> str:
        lines = []
        for metric, val in growth.items():
            pct     = val.get("growth_%", "N/A")
            insight = val.get("insight", "")
            lines.append(f"  - {metric.replace('_',' ').title()}: {pct}%  ({insight})")
        return "\n".join(lines)


    def _format_risks(self, risks: list) -> str:
        if not risks:
            return "  - No major risks detected."
        return "\n".join(f"  - {r}" for r in risks)


    def run(self, query: str, context: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        context keys:
            kpis      — dict from KPIExtractionAgent
            analysis  — dict from FinancialAnalystAgent
            company   — company name
            year      — fiscal year
        """
        try:
            kpis     = context.get("kpis",     {})
            analysis = context.get("analysis", {})
            company  = context.get("company")  or self.get_context("company") or "Unknown"
            year     = context.get("year")     or self.get_context("year")    or "Unknown"
            risks    = analysis.get("risk_flags", [])
            growth   = analysis.get("yoy_growth", {})
            date     = datetime.now().strftime("%Y-%m-%d")

            report = f"""
================================================================================
                        CFO FINANCIAL ANALYSIS REPORT
================================================================================
Company      : {company}
Fiscal Year  : {year}
Generated On : {date}
--------------------------------------------------------------------------------

1. KEY FINANCIAL METRICS
------------------------
{self._format_kpis(kpis) or "  - No KPIs extracted."}

2. FINANCIAL RATIOS & INSIGHTS
-------------------------------
{self._format_analysis(analysis) or "  - No analysis available."}

3. YEAR-OVER-YEAR GROWTH
-------------------------
{self._format_growth(growth) or "  - No growth data available."}

4. RISK FLAGS
-------------
{self._format_risks(risks)}

5. RECOMMENDATIONS
------------------
{self._generate_recommendations(analysis, risks)}

================================================================================
                              END OF REPORT
================================================================================
""".strip()

            self.remember("assistant", f"Report generated for {company} {year}")

            return self.success({
                "report" : report,
                "company": company,
                "year"   : year,
            })

        except Exception as e:
            return self.failure(str(e))


    def _generate_recommendations(self, analysis: Dict, risks: list) -> str:
        recs = []

        if "profit_margin" in analysis:
            margin = analysis["profit_margin"].get("margin_%", 0)
            if margin < 10:
                recs.append("  - Improve profit margin by reducing operating costs.")
            else:
                recs.append("  - Maintain strong profit margins through cost discipline.")

        if "debt_to_equity" in analysis:
            ratio = analysis["debt_to_equity"].get("ratio", 0)
            if ratio > 2:
                recs.append("  - Reduce debt levels to improve financial stability.")

        if "free_cash_flow" in analysis:
            fcf = analysis["free_cash_flow"].get("fcf", 0)
            if fcf > 0:
                recs.append("  - Deploy positive FCF into R&D or shareholder returns.")
            else:
                recs.append("  - Address negative FCF by optimizing CapEx spending.")

        if not recs:
            recs.append("  - Continue monitoring KPIs quarterly.")

        return "\n".join(recs)


# --- Quick test ---
if __name__ == "__main__":
    agent = ReportGenerationAgent()

    response = agent.run(
        query   = "Generate Tesla 2024 CFO report",
        context = {
            "company" : "Tesla",
            "year"    : "2024",
            "kpis"    : {
                "revenue"          : 81.4,
                "net_income"       : 10.2,
                "operating_income" : 13.7,
                "gross_profit"     : 17.5,
                "cash_flow"        : 14.9,
            },
            "analysis": {
                "profit_margin"   : {"metric": "profit_margin",    "margin_%": 12.53, "insight": "Strong"},
                "operating_margin": {"metric": "operating_margin",  "margin_%": 16.83, "insight": "Healthy"},
                "free_cash_flow"  : {"metric": "free_cash_flow",    "fcf": 6.0,        "insight": "Positive FCF"},
                "debt_to_equity"  : {"metric": "debt_to_equity",    "ratio": 0.25,     "insight": "Low"},
                "yoy_growth"      : {
                    "revenue"    : {"growth_%": 8.53,  "insight": "Growth"},
                    "net_income" : {"growth_%": 13.33, "insight": "Growth"},
                },
                "risk_flags"      : [],
            },
        }
    )

    print(response["result"]["report"])