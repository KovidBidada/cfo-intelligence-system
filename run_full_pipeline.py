# run_full_pipeline.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ingestion.pipeline import run_pipeline
from vector_store.indexer import index_chunks


# Step 1 — fetch financial data
print("Fetching financial data...")
exec(open("data/raw/fetch_financial_data.py").read())

# Step 2 — ingest all txt files
print("\nRunning ingestion pipeline...")
chunks = run_pipeline("data/raw/")
print(f"Total chunks: {len(chunks)}")

# Step 3 — index into Qdrant
index_chunks(chunks)
print("All data indexed into Qdrant.")