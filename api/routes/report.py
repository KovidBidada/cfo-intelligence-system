# api/routes/report.py

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, FileResponse
from api.schemas import ReportResponse
from agents.orchestrator import Orchestrator

router = APIRouter()

# in-memory report store
# { report_id: { company, year, report } }
REPORTS: dict = {}


@router.post("/report/generate", response_model=ReportResponse)
def generate_report(
    company : str,
    year    : str,
    user_id : str = "default_user",
    query   : str = "Generate CFO financial report",
):
    """
    Run orchestrator and store generated report.
    Returns report_id for later retrieval.
    """
    try:
        orchestrator = Orchestrator(user_id=user_id)

        response = orchestrator.run(
            query   = query,
            context = {
                "company": company,
                "year"   : year,
            }
        )

        if response["status"] == "error":
            raise HTTPException(status_code=500, detail=response["error"])

        result    = response["result"]
        report_id = f"{company.lower()}_{year}"

        # store in memory
        REPORTS[report_id] = {
            "company": company,
            "year"   : year,
            "report" : result["report"],
        }

        # save to file
        os.makedirs("data/outputs", exist_ok=True)
        file_path = f"data/outputs/{report_id}.txt"
        with open(file_path, "w") as f:
            f.write(result["report"])

        return ReportResponse(
            status  = "success",
            company = company,
            year    = year,
            report  = result["report"],
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{report_id}", response_class=PlainTextResponse)
def get_report(report_id: str):
    """Retrieve a stored report by report_id."""
    if report_id not in REPORTS:
        raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found.")

    return REPORTS[report_id]["report"]


@router.get("/report/{report_id}/download")
def download_report(report_id: str):
    """Download report as a .txt file."""
    file_path = f"data/outputs/{report_id}.txt"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Report file not found: {file_path}")

    return FileResponse(
        path             = file_path,
        media_type       = "text/plain",
        filename         = f"{report_id}_cfo_report.txt",
    )


@router.get("/reports/list")
def list_reports():
    """List all generated reports."""
    return {
        "total"  : len(REPORTS),
        "reports": [
            {"report_id": k, "company": v["company"], "year": v["year"]}
            for k, v in REPORTS.items()
        ]
    }