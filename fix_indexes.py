# fix_indexes.py

from vector_store.qdrant_client import get_client
from qdrant_client.models import PayloadSchemaType

client = get_client()

# add indexes to existing financial_documents collection
for field in ["company", "year", "section", "document_type", "financial_metric"]:
    client.create_payload_index(
        collection_name = "financial_documents",
        field_name      = field,
        field_schema    = PayloadSchemaType.KEYWORD,
    )
    print(f"Index created: {field}")

# add index to memory collection if it exists
try:
    client.create_payload_index(
        collection_name = "cfo_long_term_memory",
        field_name      = "user_id",
        field_schema    = PayloadSchemaType.KEYWORD,
    )
    print("Index created: user_id")
except:
    print("Memory collection not found — will be created on first use.")

print("\nAll indexes created.")