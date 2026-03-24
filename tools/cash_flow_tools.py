# tools/cash_flow_tools.py

from typing import Dict, Any, List


def free_cash_flow(operating_cash_flow: float, capex: float) -> Dict[str, Any]:
    """Free Cash Flow = Operating Cash Flow - CapEx"""
    fcf = operating_cash_flow - capex
    return {
        "metric"             : "free_cash_flow",
        "operating_cash_flow": operating_cash_flow,
        "capex"              : capex,
        "fcf"                : round(fcf, 2),
        "insight"            : "Positive FCF" if fcf > 0 else "Negative FCF",
    }


def operating_cash_flow_ratio(operating_cash_flow: float, current_liabilities: float) -> Dict[str, Any]:
    """How well operating cash covers short-term liabilities"""
    if current_liabilities == 0:
        return {"error": "Current liabilities cannot be zero"}
    ratio = operating_cash_flow / current_liabilities
    return {
        "metric"             : "operating_cash_flow_ratio",
        "operating_cash_flow": operating_cash_flow,
        "current_liabilities": current_liabilities,
        "ratio"              : round(ratio, 2),
        "insight"            : "Healthy" if ratio >= 1 else "Watch",
    }


def cash_flow_margin(operating_cash_flow: float, revenue: float) -> Dict[str, Any]:
    """Operating Cash Flow Margin %"""
    if revenue == 0:
        return {"error": "Revenue cannot be zero"}
    margin = (operating_cash_flow / revenue) * 100
    return {
        "metric"             : "cash_flow_margin",
        "operating_cash_flow": operating_cash_flow,
        "revenue"            : revenue,
        "margin_%"           : round(margin, 2),
    }


def capex_to_revenue(capex: float, revenue: float) -> Dict[str, Any]:
    """CapEx as % of Revenue — measures investment intensity"""
    if revenue == 0:
        return {"error": "Revenue cannot be zero"}
    ratio = (capex / revenue) * 100
    return {
        "metric" : "capex_to_revenue",
        "capex"  : capex,
        "revenue": revenue,
        "ratio_%" : round(ratio, 2),
        "insight": "High investment" if ratio > 10 else "Moderate" if ratio > 5 else "Low",
    }


def cash_flow_summary(
    operating_cash_flow : float,
    investing_cash_flow : float,
    financing_cash_flow : float,
) -> Dict[str, Any]:
    """Full cash flow statement summary"""
    net_change = operating_cash_flow + investing_cash_flow + financing_cash_flow
    return {
        "metric"             : "cash_flow_summary",
        "operating_cash_flow": operating_cash_flow,
        "investing_cash_flow": investing_cash_flow,
        "financing_cash_flow": financing_cash_flow,
        "net_cash_change"    : round(net_change, 2),
        "insight"            : "Net inflow" if net_change > 0 else "Net outflow",
    }


# --- Quick test ---
if __name__ == "__main__":
    print(free_cash_flow(operating_cash_flow=14.9, capex=8.9))
    print(operating_cash_flow_ratio(operating_cash_flow=14.9, current_liabilities=10.0))
    print(cash_flow_margin(operating_cash_flow=14.9, revenue=81.4))
    print(capex_to_revenue(capex=8.9, revenue=81.4))
    print(cash_flow_summary(
        operating_cash_flow =  14.9,
        investing_cash_flow = -8.9,
        financing_cash_flow = -3.0,
    ))