# tools/growth_calculator.py

from typing import Dict, Any, List


def yoy_growth(current: float, previous: float) -> Dict[str, Any]:
    """Year-over-year growth %"""
    if previous == 0:
        return {"error": "Previous value cannot be zero"}
    growth = ((current - previous) / previous) * 100
    return {
        "metric"   : "yoy_growth",
        "current"  : current,
        "previous" : previous,
        "growth_%" : round(growth, 2),
        "insight"  : "Growth" if growth > 0 else "Decline",
    }


def cagr(start: float, end: float, years: int) -> Dict[str, Any]:
    """Compound Annual Growth Rate %"""
    if start == 0:
        return {"error": "Start value cannot be zero"}
    if years == 0:
        return {"error": "Years cannot be zero"}
    rate = ((end / start) ** (1 / years) - 1) * 100
    return {
        "metric"  : "cagr",
        "start"   : start,
        "end"     : end,
        "years"   : years,
        "cagr_%"  : round(rate, 2),
        "insight" : f"{round(rate, 2)}% compounded annually over {years} years",
    }


def revenue_growth_series(values: List[float], years: List[str]) -> List[Dict[str, Any]]:
    """
    YoY growth for a series of revenue values.
    values = [70, 75, 81]
    years  = ["2022", "2023", "2024"]
    """
    if len(values) != len(years):
        return [{"error": "values and years must be same length"}]

    results = []
    for i in range(1, len(values)):
        growth = yoy_growth(values[i], values[i - 1])
        growth["year"] = years[i]
        results.append(growth)

    return results


def absolute_change(current: float, previous: float) -> Dict[str, Any]:
    """Absolute dollar/unit change"""
    change = current - previous
    return {
        "metric"  : "absolute_change",
        "current" : current,
        "previous": previous,
        "change"  : round(change, 2),
        "insight" : "Increased" if change > 0 else "Decreased",
    }


# --- Quick test ---
if __name__ == "__main__":
    print(yoy_growth(current=81.4, previous=75.0))
    print(cagr(start=70.0, end=81.4, years=2))
    print(absolute_change(current=81.4, previous=75.0))

    series = revenue_growth_series(
        values=[70.0, 75.0, 81.4],
        years =["2022", "2023", "2024"]
    )
    print("\nRevenue Growth Series:")
    for s in series:
        print(f"  {s['year']}: {s['growth_%']}% — {s['insight']}")