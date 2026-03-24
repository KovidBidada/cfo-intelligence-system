markdown# CFO Intelligence System

An agentic AI-powered CFO assistant that analyzes financial documents, extracts KPIs, performs ratio analysis, and generates professional CFO-level reports using multi-agent orchestration and vector retrieval.

---

## What It Does

- Ingests financial documents (PDF, DOCX, XLSX, CSV, TXT)
- Embeds and indexes them into Qdrant vector database
- Retrieves relevant financial context using semantic search
- Extracts KPIs automatically (revenue, net income, margins, etc.)
- Performs financial ratio analysis (profit margin, ROE, debt-to-equity, etc.)
- Analyzes financial tables with Pandas and DuckDB
- Generates professional CFO-level reports
- Remembers past analyses using short-term and long-term memory

---

## System Architecture
```
User Query
    │
    ▼
Orchestrator Agent
    │
    ├── Retrieval Agent        → Qdrant semantic search
    ├── KPI Extraction Agent   → Extract financial metrics
    ├── Table Reasoning Agent  → Pandas + DuckDB analysis
    ├── Financial Analyst Agent→ Ratios, trends, risk flags
    └── Report Generation Agent→ Professional CFO report
```

---

## Tech Stack

| Layer            | Technology                        |
|------------------|-----------------------------------|
| Language         | Python 3.11+                      |
| Agent Framework  | LangChain + LangGraph             |
| Vector Database  | Qdrant Cloud                      |
| Embeddings       | BGE-M3 (sentence-transformers)    |
| Data Analysis    | Pandas, DuckDB                    |
| Financial Data   | yfinance                          |
| API              | FastAPI + Uvicorn                 |
| Templates        | Jinja2                            |
| Config           | Pydantic Settings                 |

---
