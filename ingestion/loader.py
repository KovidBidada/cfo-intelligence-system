# ingestion/loader.py

import os
from pathlib import Path
from typing import List, Dict, Any

import fitz
import pdfplumber
from docx import Document
import pandas as pd


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".xls", ".csv", ".txt"}


def load_pdf(file_path: str) -> List[Dict[str, Any]]:
    pages = []
    path  = Path(file_path)
    doc   = fitz.open(file_path)

    for page_num, page in enumerate(doc):
        text = page.get_text().strip()
        if not text:
            with pdfplumber.open(file_path) as pdf:
                text = pdf.pages[page_num].extract_text() or ""

        pages.append({
            "page_number": page_num + 1,
            "text"       : text,
            "source"     : path.name,
            "file_path"  : str(path),
            "file_type"  : "pdf",
        })

    doc.close()
    return pages


def load_docx(file_path: str) -> List[Dict[str, Any]]:
    path      = Path(file_path)
    doc       = Document(file_path)
    full_text = "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())

    return [{
        "page_number": 1,
        "text"       : full_text,
        "source"     : path.name,
        "file_path"  : str(path),
        "file_type"  : "docx",
    }]


def load_excel(file_path: str) -> List[Dict[str, Any]]:
    path   = Path(file_path)
    pages  = []
    xl     = pd.ExcelFile(file_path)

    for i, sheet in enumerate(xl.sheet_names):
        df   = xl.parse(sheet)
        text = f"Sheet: {sheet}\n{df.to_string(index=False)}"
        pages.append({
            "page_number": i + 1,
            "text"       : text,
            "source"     : path.name,
            "file_path"  : str(path),
            "file_type"  : "xlsx",
            "sheet_name" : sheet,
        })

    return pages


def load_csv(file_path: str) -> List[Dict[str, Any]]:
    path = Path(file_path)
    df   = pd.read_csv(file_path)

    return [{
        "page_number": 1,
        "text"       : df.to_string(index=False),
        "source"     : path.name,
        "file_path"  : str(path),
        "file_type"  : "csv",
    }]


def load_txt(file_path: str) -> List[Dict[str, Any]]:
    path = Path(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    return [{
        "page_number": 1,
        "text"       : text,
        "source"     : path.name,
        "file_path"  : str(path),
        "file_type"  : "txt",
    }]


def load_document(file_path: str) -> List[Dict[str, Any]]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = path.suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    if ext == ".pdf"            : return load_pdf(file_path)
    elif ext == ".docx"         : return load_docx(file_path)
    elif ext in (".xlsx", ".xls"): return load_excel(file_path)
    elif ext == ".csv"          : return load_csv(file_path)
    elif ext == ".txt"          : return load_txt(file_path)


def load_directory(dir_path: str) -> List[Dict[str, Any]]:
    all_pages = []
    directory = Path(dir_path)

    for file_path in sorted(directory.iterdir()):
        if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            print(f"  Loading: {file_path.name}")
            pages = load_document(str(file_path))
            all_pages.extend(pages)

    return all_pages


if __name__ == "__main__":
    import sys
    path  = sys.argv[1] if len(sys.argv) > 1 else "data/raw"
    pages = load_directory(path) if os.path.isdir(path) else load_document(path)
    print(f"Loaded {len(pages)} pages")
    for p in pages[:2]:
        print(f"\n--- {p['source']} ---")
        print(p["text"][:300])