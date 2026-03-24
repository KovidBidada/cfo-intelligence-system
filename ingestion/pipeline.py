# ingestion/pipeline.py

from ingestion.loader import load_document, load_directory
from ingestion.chunker import chunk_pages
from ingestion.embedder import embed_chunks
from ingestion.metadata_extractor import extract_metadata_batch


def run_pipeline(path: str) -> list:
    """
    Full ingestion pipeline for a single file or directory.
    Returns final chunks ready for vector store indexing.
    """
    import os

    print(f"\n[1/4] Loading documents from: {path}")
    if os.path.isdir(path):
        pages = load_directory(path)
    else:
        pages = load_document(path)
    print(f"      Loaded {len(pages)} pages")

    print(f"\n[2/4] Chunking pages...")
    chunks = chunk_pages(pages)
    print(f"      Created {len(chunks)} chunks")

    print(f"\n[3/4] Embedding chunks...")
    chunks = embed_chunks(chunks)
    print(f"      Embedded {len(chunks)} chunks")

    print(f"\n[4/4] Extracting metadata...")
    chunks = extract_metadata_batch(chunks)
    print(f"      Metadata extracted for {len(chunks)} chunks")

    print(f"\nPipeline complete. {len(chunks)} chunks ready for indexing.\n")
    return chunks


# --- Quick test ---
if __name__ == "__main__":
    import sys

    path   = sys.argv[1] if len(sys.argv) > 1 else "data/raw"
    chunks = run_pipeline(path)

    print(f"Sample chunk:")
    print(f"  chunk_id        : {chunks[0]['chunk_id']}")
    print(f"  company         : {chunks[0]['company']}")
    print(f"  year            : {chunks[0]['year']}")
    print(f"  document_type   : {chunks[0]['document_type']}")
    print(f"  section         : {chunks[0]['section']}")
    print(f"  embedding dim   : {len(chunks[0]['embedding'])}")