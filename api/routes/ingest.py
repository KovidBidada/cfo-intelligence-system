# api/routes/ingest.py

from fastapi import APIRouter, HTTPException
from api.schemas import IngestRequest, IngestResponse
from ingestion.pipeline import run_pipeline
from vector_store.indexer import index_chunks

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
def ingest_document(request: IngestRequest):
    """
    Load → Chunk → Embed → Extract Metadata → Index into Qdrant
    """
    try:
        print(f"[Ingest] Starting pipeline for: {request.file_path}")

        # run full ingestion pipeline
        chunks = run_pipeline(request.file_path)

        # override company + year if provided
        if request.company or request.year:
            for chunk in chunks:
                if request.company:
                    chunk["company"] = request.company
                if request.year:
                    chunk["year"] = request.year

        # index into Qdrant
        index_chunks(chunks)

        return IngestResponse(
            status       = "success",
            file_path    = request.file_path,
            total_chunks = len(chunks),
            message      = f"Successfully indexed {len(chunks)} chunks into Qdrant.",
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))