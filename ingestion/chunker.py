# ingestion/chunker.py

from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_pages(pages: List[Dict[str, Any]], chunk_size: int = 600, chunk_overlap: int = 100) -> List[Dict[str, Any]]:
    """
    Takes pages from loader.py and splits text into chunks.
    Returns list of chunk dicts with metadata preserved.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = []

    for page in pages:
        text = page["text"].strip()
        if not text:
            continue

        splits = splitter.split_text(text)

        for i, split in enumerate(splits):
            chunks.append({
                "chunk_id"    : f"{page['source']}_p{page['page_number']}_c{i}",
                "text"        : split,
                "source"      : page["source"],
                "file_path"   : page["file_path"],
                "file_type"   : page["file_type"],
                "page_number" : page["page_number"],
                "chunk_index" : i,
            })

    return chunks