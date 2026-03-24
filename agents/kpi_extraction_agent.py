# agents/kpi_extraction_agent.py

import re
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from memory.short_term import ShortTermMemory


KPI_PATTERNS = {
    # standard formats: Revenue: $81.4B
    "revenue"          : r"(?:total\s+)?revenue[:\s]+\$?([\d,.]+)\s*([BbMm]?)",
    "net_income"       : r"net income[:\s]+\$?([\d,.]+)\s*([BbMm]?)",
    "gross_profit"     : r"gross profit[s]?[:\s]+\$?([\d,.]+)\s*([BbMm]?)",
    "operating_income" : r"operating income[:\s]+\$?([\d,.]+)\s*([BbMm]?)",
    "ebitda"           : r"ebitda[:\s]+\$?([\d,.]+)\s*([BbMm]?)",
    "cash_flow"        : r"(?:operating\s+)?cash(?:flow| flow)[:\s]+\$?([\d,.]+)\s*([BbMm]?)",
    "free_cash_flow"   : r"free cash(?:flow| flow)[:\s]+\$?([\d,.]+)\s*([BbMm]?)",
    "total_debt"       : r"total debt[:\s]+\$?([\d,.]+)\s*([BbMm]?)",
    "total_equity"     : r"total equity[:\s]+\$?([\d,.]+)\s*([BbMm]?)",
    "current_assets"   : r"current assets[:\s]+\$?([\d,.]+)\s*([BbMm]?)",
    "current_liabilities": r"current liabilities[:\s]+\$?([\d,.]+)\s*([BbMm]?)",
    "eps"              : r"eps[:\s]+\$?([\d,.]+)",
    "capex"            : r"cap(?:ital )?ex(?:penditure)?[:\s]+\$?([\d,.]+)\s*([BbMm]?)",

    # percentage formats: Gross Margin: 17.5%
    "gross_margin"     : r"gross margin[:\s]+([\d,.]+)\s*%?",
    "net_margin"       : r"(?:net|profit) margin[:\s]+([\d,.]+)\s*%?",
    "operating_margin" : r"operating margin[:\s]+([\d,.]+)\s*%?",
    "return_on_equity" : r"return on equity[:\s]+([\d,.]+)\s*%?",

    # large number formats from yfinance: 97690000000
    "revenue_raw"      : r"(?:total\s+)?revenue\s*[:\s]+([\d]{6,})",
    "net_income_raw"   : r"net income\s*[:\s]+([\d]{6,})",
}


def _normalize(value: str, unit: str) -> float:
    """Convert string value + unit to float in billions."""
    v    = float(value.replace(",", ""))
    unit = unit.upper() if unit else ""

    if unit == "B":
        return round(v, 4)
    if unit == "M":
        return round(v / 1000, 4)
    # raw large numbers from yfinance (e.g. 97690000000)
    if v > 1_000_000_000:
        return round(v / 1_000_000_000, 4)
    if v > 1_000_000:
        return round(v / 1_000_000, 4)
    return round(v, 4)


def extract_kpis(text: str) -> Dict[str, Any]:
    kpis = {}

    for kpi, pattern in KPI_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            value  = groups[0]
            unit   = groups[1] if len(groups) > 1 else ""

            # skip if already have cleaner version
            base_kpi = kpi.replace("_raw", "")
            if "_raw" in kpi and base_kpi in kpis:
                continue

            try:
                normalized = _normalize(value, unit)
                # store under base name
                kpis[base_kpi] = normalized
            except:
                kpis[base_kpi] = value

    return kpis


class KPIExtractionAgent(BaseAgent):
    """
    Extracts financial KPIs from retrieved text chunks.
    Never fails — returns partial results if some KPIs found.
    """

    def __init__(self, memory: Optional[ShortTermMemory] = None):
        super().__init__(name="KPIExtractionAgent", memory=memory)


    def run(self, query: str, context: Dict[str, Any] = {}) -> Dict[str, Any]:
        try:
            chunks       = context.get("chunks", [])
            context_text = context.get("context_text", "")

            full_text = context_text or "\n".join(c["text"] for c in chunks)

            if not full_text.strip():
                return self.failure("No text provided for KPI extraction.")

            kpis = extract_kpis(full_text)

            # never fail — return empty dict with warning if no KPIs
            if not kpis:
                print(f"  [KPIAgent] Warning: No KPIs found, continuing with empty dict.")
                kpis = {}

            self.remember("assistant", f"Extracted KPIs: {list(kpis.keys())}")

            return self.success({
                "kpis" : kpis,
                "total": len(kpis),
            })

        except Exception as e:
            return self.failure(str(e))