# ingestion/metadata_extractor.py

import re
from typing import Dict, Any


COMPANY_KEYWORDS = [
    "tesla", "apple", "microsoft", "google", "amazon",
    "meta", "nvidia", "netflix", "uber", "airbnb"
]

DOCUMENT_TYPES = {
    "annual report"      : "annual_report",
    "10-k"               : "annual_report",
    "quarterly report"   : "quarterly_report",
    "10-q"               : "quarterly_report",
    "earnings"           : "earnings_report",
    "balance sheet"      : "balance_sheet",
    "cash flow"          : "cash_flow",
    "income statement"   : "income_statement",
    "investor presentation": "investor_presentation",
}

SECTIONS = {
    "revenue"            : "revenue",
    "operating income"   : "operating_income",
    "net income"         : "net_income",
    "gross profit"       : "gross_profit",
    "ebitda"             : "ebitda",
    "cash flow"          : "cash_flow",
    "operating expenses" : "operating_expenses",
    "risk"               : "risk_factors",
    "balance sheet"      : "balance_sheet",
}


def extract_company(text: str) -> str:
    text_lower = text.lower()
    for company in COMPANY_KEYWORDS:
        if company in text_lower:
            return company.capitalize()
    return "Unknown"


def extract_year(text: str) -> str:
    match = re.search(r"\b(20\d{2})\b", text)
    return match.group(1) if match else "Unknown"


def extract_document_type(text: str) -> str:
    text_lower = text.lower()
    for keyword, doc_type in DOCUMENT_TYPES.items():
        if keyword in text_lower:
            return doc_type
    return "general"


def extract_section(text: str) -> str:
    text_lower = text.lower()
    for keyword, section in SECTIONS.items():
        if keyword in text_lower:
            return section
    return "general"


def extract_financial_metric(text: str) -> str:
    patterns = {
        "revenue"       : r"revenue[:\s]+\$?([\d,.]+[BbMm]?)",
        "net_income"    : r"net income[:\s]+\$?([\d,.]+[BbMm]?)",
        "gross_profit"  : r"gross profit[:\s]+\$?([\d,.]+[BbMm]?)",
        "ebitda"        : r"ebitda[:\s]+\$?([\d,.]+[BbMm]?)",
    }
    for metric, pattern in patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            return metric
    return "none"


def extract_metadata(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes a chunk from chunker.py, extracts financial metadata.
    Returns chunk with metadata fields added.
    """
    text = chunk["text"]

    chunk["company"]          = extract_company(text)
    chunk["year"]             = extract_year(text)
    chunk["document_type"]    = extract_document_type(text)
    chunk["section"]          = extract_section(text)
    chunk["financial_metric"] = extract_financial_metric(text)

    return chunk


def extract_metadata_batch(chunks: list) -> list:
    return [extract_metadata(chunk) for chunk in chunks]


# --- Quick test ---
if __name__ == "__main__":
    sample_chunk = {
        "chunk_id"   : "tesla_2024_p1_c0",
        "text"       : "Tesla Annual Report 2024. Revenue: $81.4B. Net Income: $10.2B. Operating expenses rose.",
        "source"     : "tesla_2024.pdf",
        "file_path"  : "data/raw/tesla_2024.pdf",
        "file_type"  : "pdf",
        "page_number": 1,
        "chunk_index": 0,
    }

    result = extract_metadata(sample_chunk)
    print(f"Company         : {result['company']}")
    print(f"Year            : {result['year']}")
    print(f"Document type   : {result['document_type']}")
    print(f"Section         : {result['section']}")
    print(f"Financial metric: {result['financial_metric']}")