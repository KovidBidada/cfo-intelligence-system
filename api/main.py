# api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import ingest, analyze, report

app = FastAPI(
    title       = "CFO Intelligence System",
    description = "Agentic AI CFO assistant powered by Qdrant + Multi-Agent Orchestration",
    version     = "1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# routers
app.include_router(ingest.router,  prefix="/api/v1", tags=["Ingestion"])
app.include_router(analyze.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(report.router,  prefix="/api/v1", tags=["Report"])


@app.get("/")
def root():
    return {
        "app"    : "CFO Intelligence System",
        "version": "1.0.0",
        "status" : "running",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Run ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)