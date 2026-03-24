# api/routes/analyze.py

from fastapi import APIRouter, HTTPException
from api.schemas import AnalyzeRequest, AnalyzeResponse, ErrorResponse
from agents.orchestrator import Orchestrator

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    """
    Run full agent pipeline:
    Retrieve → KPI → Table → Analyst → Report
    """
    try:
        print(f"[Analyze] Query: {request.query} | User: {request.user_id}")

        orchestrator = Orchestrator(user_id=request.user_id)

        response = orchestrator.run(
            query   = request.query,
            context = {
                "company"   : request.company,
                "year"      : request.year,
                "table_data": request.table_data,
                "prev_kpis" : request.prev_kpis,
            }
        )

        if response["status"] == "error":
            raise HTTPException(status_code=500, detail=response["error"])

        result = response["result"]

        return AnalyzeResponse(
            status        = "success",
            query         = request.query,
            kpis          = result["kpis"],
            analysis      = result["analysis"],
            table_results = result["table_results"],
            report        = result["report"],
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))