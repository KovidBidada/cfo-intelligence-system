# agents/orchestrator.py

from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from agents.retrieval_agent import RetrievalAgent
from agents.kpi_extraction_agent import KPIExtractionAgent
from agents.table_reasoning_agent import TableReasoningAgent
from agents.financial_analyst_agent import FinancialAnalystAgent
from agents.report_generation_agent import ReportGenerationAgent
from memory.short_term import ShortTermMemory
from memory.long_term import save_memory, recall_memory


class Orchestrator(BaseAgent):

    def __init__(self, user_id: str = "default_user"):
        super().__init__(name="Orchestrator")
        self.user_id  = user_id
        self.memory   = ShortTermMemory()

        self.retrieval = RetrievalAgent(memory=self.memory)
        self.kpi       = KPIExtractionAgent(memory=self.memory)
        self.table     = TableReasoningAgent(memory=self.memory)
        self.analyst   = FinancialAnalystAgent(memory=self.memory)
        self.reporter  = ReportGenerationAgent(memory=self.memory)


    def run(self, query: str, context: Dict[str, Any] = {}) -> Dict[str, Any]:
        try:
            print(f"\n{'='*60}")
            print(f"[Orchestrator] Query: {query}")
            print(f"{'='*60}")

            company    = context.get("company")
            year       = context.get("year")
            table_data = context.get("table_data")

            if company:
                self.memory.set_context("company", company)
            if year:
                self.memory.set_context("year", year)

            # recall long-term memory
            past = recall_memory(self.user_id, query, top_k=3)
            if past:
                print(f"[Orchestrator] Recalled {len(past)} past memories")

            # --- Step 1: Retrieval ---
            print(f"\n[Step 1] Retrieval Agent")
            retrieval_resp = self.retrieval.run(query, context)
            if retrieval_resp["status"] == "error":
                return self.failure(f"Retrieval failed: {retrieval_resp['error']}")

            retrieval_result = retrieval_resp["result"]
            print(f"  Retrieved {retrieval_result['total']} chunks")

            # --- Step 2: KPI Extraction ---
            print(f"[Step 2] KPI Extraction Agent")
            kpi_resp = self.kpi.run(query, {
                "chunks"      : retrieval_result["chunks"],
                "context_text": retrieval_result["context_text"],
            })

            # never block on KPI failure — continue with empty
            kpis = {}
            if kpi_resp["status"] == "success":
                kpis = kpi_resp["result"]["kpis"]
            print(f"  KPIs extracted: {list(kpis.keys()) if kpis else 'none — continuing'}")

            # --- Step 3: Table Reasoning ---
            table_results = {}
            if table_data:
                print(f"[Step 3] Table Reasoning Agent")
                table_resp = self.table.run(query, {
                    "table_data": table_data,
                    "value_col" : context.get("value_col", "revenue"),
                    "year_col"  : context.get("year_col",  "year"),
                })
                if table_resp["status"] == "success":
                    table_results = table_resp["result"]["results"]
            else:
                print(f"[Step 3] Table Reasoning — skipped")

            # --- Step 4: Financial Analysis ---
            print(f"[Step 4] Financial Analyst Agent")
            analyst_resp = self.analyst.run(query, {
                "kpis"     : kpis,
                "prev_kpis": context.get("prev_kpis", {}),
            })

            # never block on analyst failure
            analysis = {}
            if analyst_resp["status"] == "success":
                analysis = analyst_resp["result"]["analysis"]
            print(f"  Analysis done: {list(analysis.keys()) if analysis else 'none — continuing'}")

            # --- Step 5: Report Generation ---
            print(f"[Step 5] Report Generation Agent")
            report_resp = self.reporter.run(query, {
                "company" : company,
                "year"    : year,
                "kpis"    : kpis,
                "analysis": analysis,
            })
            if report_resp["status"] == "error":
                return self.failure(f"Report failed: {report_resp['error']}")

            report = report_resp["result"]["report"]

            # save to long-term memory
            save_memory(
                self.user_id,
                f"Analyzed {company} {year}: revenue={kpis.get('revenue')} net_income={kpis.get('net_income')}",
                tags={"company": company or "", "year": year or "", "topic": "analysis"}
            )

            print(f"\n[Orchestrator] Pipeline complete.")

            return self.success({
                "query"        : query,
                "kpis"         : kpis,
                "analysis"     : analysis,
                "table_results": table_results,
                "report"       : report,
            })

        except Exception as e:
            return self.failure(str(e))


# --- Quick test ---
if __name__ == "__main__":
    orchestrator = Orchestrator(user_id="user_001")

    response = orchestrator.run(
        query   = "Analyze Tesla revenue and profit for 2024",
        context = {
            "company"   : "Tesla",
            "year"      : "2024",
            "table_data": [
                {"year": "2022", "revenue": 70.0, "net_income": 8.0},
                {"year": "2023", "revenue": 75.0, "net_income": 9.0},
                {"year": "2024", "revenue": 81.4, "net_income": 10.2},
            ],
            "prev_kpis": {
                "revenue"   : 75.0,
                "net_income": 9.0,
            }
        }
    )

    print(f"\nStatus : {response['status']}")

    if response["status"] == "error":
        print(f"Error  : {response['error']}")
    else:
        print(f"KPIs   : {response['result']['kpis']}")
        print(f"\n{response['result']['report']}")