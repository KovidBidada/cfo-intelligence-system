# memory/long_term.py

import uuid
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue

from vector_store.qdrant_client import get_client, create_memory_collection, MEMORY_COLLECTION_NAME
from ingestion.embedder import model


MEMORY_COLLECTION = MEMORY_COLLECTION_NAME


def _ensure_collection(client: QdrantClient) -> None:
    create_memory_collection(client)


def save_memory(
    user_id : str,
    content : str,
    tags    : Dict[str, str] = {},
    client  : Optional[QdrantClient] = None,
) -> None:
    if client is None:
        client = get_client()

    _ensure_collection(client)

    vector = model.encode(content, normalize_embeddings=True).tolist()

    client.upsert(
        collection_name = MEMORY_COLLECTION,
        points          = [PointStruct(
            id      = str(uuid.uuid4()),
            vector  = vector,
            payload = {"user_id": user_id, "content": content, **tags}
        )]
    )


def recall_memory(
    user_id : str,
    query   : str,
    top_k   : int = 5,
    client  : Optional[QdrantClient] = None,
) -> List[Dict[str, Any]]:
    if client is None:
        client = get_client()

    _ensure_collection(client)

    vector = model.encode(query, normalize_embeddings=True).tolist()

    results = client.query_points(
        collection_name = MEMORY_COLLECTION,
        query           = vector,
        query_filter    = Filter(must=[
            FieldCondition(key="user_id", match=MatchValue(value=user_id))
        ]),
        limit           = top_k,
        with_payload    = True,
    ).points

    return [
        {"score": round(r.score, 4), **r.payload}
        for r in results
    ]


def delete_memory(user_id: str, client: Optional[QdrantClient] = None) -> None:
    if client is None:
        client = get_client()

    client.delete(
        collection_name = MEMORY_COLLECTION,
        points_selector = Filter(must=[
            FieldCondition(key="user_id", match=MatchValue(value=user_id))
        ])
    )
    print(f"Deleted all memories for user: {user_id}")