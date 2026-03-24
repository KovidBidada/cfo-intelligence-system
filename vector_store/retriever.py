# vector_store/retriever.py

from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from vector_store.qdrant_client import get_client, COLLECTION_NAME
from ingestion.embedder import model


def embed_query(query: str) -> list:
    vector = model.encode(query, normalize_embeddings=True)
    return vector.tolist()


def build_filter(
    company : Optional[str] = None,
    year    : Optional[str] = None,
    section : Optional[str] = None,
    doc_type: Optional[str] = None,
) -> Optional[Filter]:
    conditions = []

    if company:
        conditions.append(FieldCondition(key="company", match=MatchValue(value=company)))
    if year:
        conditions.append(FieldCondition(key="year",    match=MatchValue(value=year)))
    if section:
        conditions.append(FieldCondition(key="section", match=MatchValue(value=section)))
    if doc_type:
        conditions.append(FieldCondition(key="document_type", match=MatchValue(value=doc_type)))

    return Filter(must=conditions) if conditions else None


def retrieve(
    query   : str,
    top_k   : int = 5,
    company : Optional[str] = None,
    year    : Optional[str] = None,
    section : Optional[str] = None,
    doc_type: Optional[str] = None,
    client  : Optional[QdrantClient] = None,
) -> List[Dict[str, Any]]:
    if client is None:
        client = get_client()

    query_vector = query_vector = embed_query(query)

    # Stage 1 — try with filters first
    filters = build_filter(company, year, section, doc_type)
    results = client.query_points(
        collection_name = COLLECTION_NAME,
        query           = query_vector,
        query_filter    = filters,
        limit           = top_k,
        with_payload    = True,
    ).points

    # Stage 2 — fallback: search without year filter
    if not results and year:
        print(f"  [Retriever] No results with year filter, retrying without year...")
        filters = build_filter(company, None, section, doc_type)
        results = client.query_points(
            collection_name = COLLECTION_NAME,
            query           = query_vector,
            query_filter    = filters,
            limit           = top_k,
            with_payload    = True,
        ).points

    # Stage 3 — fallback: search without any filters
    if not results:
        print(f"  [Retriever] No results with filters, retrying without filters...")
        results = client.query_points(
            collection_name = COLLECTION_NAME,
            query           = query_vector,
            limit           = top_k,
            with_payload    = True,
        ).points

    chunks = []
    for hit in results:
        chunks.append({
            "score"           : round(hit.score, 4),
            "text"            : hit.payload.get("text", ""),
            "source"          : hit.payload.get("source", ""),
            "company"         : hit.payload.get("company", ""),
            "year"            : hit.payload.get("year", ""),
            "section"         : hit.payload.get("section", ""),
            "document_type"   : hit.payload.get("document_type", ""),
            "financial_metric": hit.payload.get("financial_metric", ""),
            "page_number"     : hit.payload.get("page_number", 0),
        })

    return chunks


# --- Quick test ---
if __name__ == "__main__":
    results = retrieve(
        query   = "Tesla revenue profit 2024",
        top_k   = 5,
        company = "Tesla",
    )

    print(f"Found {len(results)} chunks\n")
    for i, r in enumerate(results):
        print(f"[{i+1}] Score  : {r['score']}")
        print(f"     Source : {r['source']}")
        print(f"     Company: {r['company']}")
        print(f"     Text   : {r['text'][:200]}\n")