# api/schemas.py

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


# --- Ingest ---

class IngestRequest(BaseModel):
    file_path : str
    company   : Optional[str] = None
    year      : Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "data/raw/tesla_2024.pdf",
                "company"  : "Tesla",
                "year"     : "2024",
            }
        }


class IngestResponse(BaseModel):
    status       : str
    file_path    : str
    total_chunks : int
    message      : str


# --- Analyze ---

class AnalyzeRequest(BaseModel):
    query      : str
    company    : Optional[str] = None
    year       : Optional[str] = None
    user_id    : Optional[str] = "default_user"
    table_data : Optional[List[Dict[str, Any]]] = None
    prev_kpis  : Optional[Dict[str, float]]     = None

    class Config:
        json_schema_extra = {
            "example": {
                "query"     : "Analyze Tesla revenue and profit for 2024",
                "company"   : "Tesla",
                "year"      : "2024",
                "user_id"   : "user_001",
                "table_data": [
                    {"year": "2022", "revenue": 70.0, "net_income": 8.0},
                    {"year": "2023", "revenue": 75.0, "net_income": 9.0},
                    {"year": "2024", "revenue": 81.4, "net_income": 10.2},
                ],
                "prev_kpis" : {
                    "revenue"   : 75.0,
                    "net_income": 9.0,
                }
            }
        }


class AnalyzeResponse(BaseModel):
    status       : str
    query        : str
    kpis         : Dict[str, Any]
    analysis     : Dict[str, Any]
    table_results: Dict[str, Any]
    report       : str


# --- Report ---

class ReportResponse(BaseModel):
    status  : str
    company : str
    year    : str
    report  : str


# --- Error ---

class ErrorResponse(BaseModel):
    status  : str  = "error"
    message : str