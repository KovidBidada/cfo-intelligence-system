# vector_store/qdrant_client.py

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType
from config.settings import settings


COLLECTION_NAME        = "financial_documents"
MEMORY_COLLECTION_NAME = "cfo_long_term_memory"
VECTOR_DIM             = 1024


def get_client() -> QdrantClient:
    return QdrantClient(
        url     = f"https://{settings.QDRANT_HOST}",
        api_key = settings.QDRANT_API_KEY,
    )


def create_collection(client: QdrantClient) -> None:
    existing = [c.name for c in client.get_collections().collections]

    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name = COLLECTION_NAME,
            vectors_config  = VectorParams(
                size     = VECTOR_DIM,
                distance = Distance.COSINE,
            ),
        )
        print(f"Collection '{COLLECTION_NAME}' created.")

        # create payload indexes for filtered fields
        for field in ["company", "year", "section", "document_type", "financial_metric"]:
            client.create_payload_index(
                collection_name = COLLECTION_NAME,
                field_name      = field,
                field_schema    = PayloadSchemaType.KEYWORD,
            )
            print(f"  Index created: {field}")
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists.")


def create_memory_collection(client: QdrantClient) -> None:
    existing = [c.name for c in client.get_collections().collections]

    if MEMORY_COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name = MEMORY_COLLECTION_NAME,
            vectors_config  = VectorParams(
                size     = VECTOR_DIM,
                distance = Distance.COSINE,
            ),
        )
        print(f"Memory collection '{MEMORY_COLLECTION_NAME}' created.")

        # create index for user_id filter
        client.create_payload_index(
            collection_name = MEMORY_COLLECTION_NAME,
            field_name      = "user_id",
            field_schema    = PayloadSchemaType.KEYWORD,
        )
        print(f"  Index created: user_id")
    else:
        print(f"Memory collection '{MEMORY_COLLECTION_NAME}' already exists.")


def get_collection_info(client: QdrantClient) -> None:
    info = client.get_collection(COLLECTION_NAME)
    print(f"Collection : {COLLECTION_NAME}")
    print(f"Vectors    : {info.vectors_count}")
    print(f"Status     : {info.status}")


# --- Quick test ---
if __name__ == "__main__":
    client = get_client()
    create_collection(client)
    create_memory_collection(client)
    get_collection_info(client)