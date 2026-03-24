# tools/financial_ratios.py

from typing import Dict, Any


def profit_margin(revenue: float, net_income: float) -> Dict[str, Any]:
    """Net profit margin %"""
    if revenue == 0:
        return {"error": "Revenue cannot be zero"}
    margin = (net_income / revenue) * 100
    return {
        "metric"    : "profit_margin",
        "revenue"   : revenue,
        "net_income": net_income,
        "margin_%"  : round(margin, 2),
        "insight"   : f"For every $1 of revenue, ${round(net_income/revenue, 4)} is profit"
    }


def gross_margin(revenue: float, cogs: float) -> Dict[str, Any]:
    """Gross profit margin %"""
    if revenue == 0:
        return {"error": "Revenue cannot be zero"}
    gross_profit = revenue - cogs
    margin       = (gross_profit / revenue) * 100
    return {
        "metric"      : "gross_margin",
        "revenue"     : revenue,
        "cogs"        : cogs,
        "gross_profit": round(gross_profit, 2),
        "margin_%"    : round(margin, 2),
    }


def operating_margin(revenue: float, operating_income: float) -> Dict[str, Any]:
    """Operating profit margin %"""
    if revenue == 0:
        return {"error": "Revenue cannot be zero"}
    margin = (operating_income / revenue) * 100
    return {
        "metric"          : "operating_margin",
        "revenue"         : revenue,
        "operating_income": operating_income,
        "margin_%"        : round(margin, 2),
    }


def debt_to_equity(total_debt: float, total_equity: float) -> Dict[str, Any]:
    """Debt-to-equity ratio"""
    if total_equity == 0:
        return {"error": "Equity cannot be zero"}
    ratio = total_debt / total_equity
    return {
        "metric"      : "debt_to_equity",
        "total_debt"  : total_debt,
        "total_equity": total_equity,
        "ratio"       : round(ratio, 2),
        "insight"     : "High" if ratio > 2 else "Moderate" if ratio > 1 else "Low",
    }


def current_ratio(current_assets: float, current_liabilities: float) -> Dict[str, Any]:
    """Liquidity ratio"""
    if current_liabilities == 0:
        return {"error": "Current liabilities cannot be zero"}
    ratio = current_assets / current_liabilities
    return {
        "metric"             : "current_ratio",
        "current_assets"     : current_assets,
        "current_liabilities": current_liabilities,
        "ratio"              : round(ratio, 2),
        "insight"            : "Healthy" if ratio >= 1.5 else "Watch" if ratio >= 1 else "Risk",
    }


def return_on_equity(net_income: float, total_equity: float) -> Dict[str, Any]:
    """ROE %"""
    if total_equity == 0:
        return {"error": "Equity cannot be zero"}
    roe = (net_income / total_equity) * 100
    return {
        "metric"      : "return_on_equity",
        "net_income"  : net_income,
        "total_equity": total_equity,
        "roe_%"       : round(roe, 2),
    }


# --- Quick test ---
if __name__ == "__main__":
    print(profit_margin  (revenue=81.4,  net_income=10.2))
    print(gross_margin   (revenue=81.4,  cogs=45.0))
    print(operating_margin(revenue=81.4, operating_income=13.7))
    print(debt_to_equity (total_debt=5.0, total_equity=20.0))
    print(current_ratio  (current_assets=30.0, current_liabilities=15.0))
    print(return_on_equity(net_income=10.2, total_equity=20.0))