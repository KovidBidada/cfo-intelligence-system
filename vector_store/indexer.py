# vector_store/indexer.py

import uuid
import time
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from vector_store.qdrant_client import get_client, create_collection, COLLECTION_NAME


def index_chunks(chunks: List[Dict[str, Any]], client: QdrantClient = None) -> None:
    if client is None:
        client = get_client()

    create_collection(client)

    points = []
    for chunk in chunks:
        point = PointStruct(
            id      = str(uuid.uuid4()),
            vector  = chunk["embedding"],
            payload = {
                "chunk_id"        : chunk["chunk_id"],
                "text"            : chunk["text"],
                "source"          : chunk["source"],
                "file_type"       : chunk["file_type"],
                "page_number"     : chunk["page_number"],
                "chunk_index"     : chunk["chunk_index"],
                "company"         : chunk["company"],
                "year"            : chunk["year"],
                "document_type"   : chunk["document_type"],
                "section"         : chunk["section"],
                "financial_metric": chunk["financial_metric"],
            }
        )
        points.append(point)

    # smaller batch size + retry logic for cloud uploads
    batch_size  = 10
    max_retries = 3

    for i in range(0, len(points), batch_size):
        batch       = points[i : i + batch_size]
        batch_num   = i // batch_size + 1
        total_batch = (len(points) + batch_size - 1) // batch_size

        for attempt in range(1, max_retries + 1):
            try:
                client.upsert(
                    collection_name = COLLECTION_NAME,
                    points          = batch,
                    wait            = True,
                )
                print(f"  Batch {batch_num}/{total_batch} indexed ({len(batch)} chunks)")
                time.sleep(0.5)   # small delay between batches
                break

            except Exception as e:
                print(f"  Batch {batch_num} attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    wait = attempt * 3
                    print(f"  Retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    print(f"  Batch {batch_num} failed after {max_retries} attempts. Skipping.")

    print(f"\nTotal indexed: {len(points)} chunks into '{COLLECTION_NAME}'")


if __name__ == "__main__":
    from ingestion.pipeline import run_pipeline
    chunks = run_pipeline("data/raw/")
    client = get_client()
    index_chunks(chunks, client)