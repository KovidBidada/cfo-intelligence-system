# ingestion/embedder.py

from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-m3"
model = SentenceTransformer(MODEL_NAME)


def embed_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Takes chunks from chunker.py, adds embedding vector to each chunk.
    Returns same chunks with 'embedding' key added.
    """
    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    for chunk, vector in zip(chunks, embeddings):
        chunk["embedding"] = vector.tolist()

    return chunks


# --- Quick test ---
if __name__ == "__main__":
    sample_chunks = [
        {"chunk_id": "test_p1_c0", "text": "Revenue: $81.4B", "source": "test.pdf",
         "file_path": "data/raw/test.pdf", "file_type": "pdf", "page_number": 1, "chunk_index": 0},
        {"chunk_id": "test_p1_c1", "text": "Net Income: $10.2B", "source": "test.pdf",
         "file_path": "data/raw/test.pdf", "file_type": "pdf", "page_number": 1, "chunk_index": 1},
    ]

    embedded = embed_chunks(sample_chunks)
    print(f"Total chunks embedded: {len(embedded)}")
    print(f"Embedding dimension  : {len(embedded[0]['embedding'])}")
    print(f"Sample chunk_id      : {embedded[0]['chunk_id']}")