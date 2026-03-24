# reports/generator.py

import os
from datetime import datetime
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader


TEMPLATE_DIR  = "reports/templates"
OUTPUT_DIR    = "data/outputs"
TEMPLATE_FILE = "cfo_report.md.jinja"


def render_report(
    company  : str,
    year     : str,
    kpis     : Dict[str, Any],
    analysis : Dict[str, Any],
) -> str:
    """Render report from Jinja2 template."""
    env      = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(TEMPLATE_FILE)

    return template.render(
        company   = company,
        year      = year,
        kpis      = kpis,
        analysis  = analysis,
        risks     = analysis.get("risk_flags", []),
        growth    = analysis.get("yoy_growth", {}),
        date      = datetime.now().strftime("%Y-%m-%d"),
    )


def save_report(report: str, company: str, year: str, fmt: str = "txt") -> str:
    """Save report to file. Returns saved file path."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    report_id = f"{company.lower()}_{year}"
    file_path = f"{OUTPUT_DIR}/{report_id}_report.{fmt}"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Report saved: {file_path}")
    return file_path


def generate_and_save(
    company  : str,
    year     : str,
    kpis     : Dict[str, Any],
    analysis : Dict[str, Any],
    fmt      : str = "txt",
) -> Dict[str, Any]:
    """Render + save report. Returns report text + file path."""
    report    = render_report(company, year, kpis, analysis)
    file_path = save_report(report, company, year, fmt)

    return {
        "report"   : report,
        "file_path": file_path,
        "company"  : company,
        "year"     : year,
    }


# --- Quick test ---
if __name__ == "__main__":
    result = generate_and_save(
        company  = "Tesla",
        year     = "2024",
        kpis     = {
            "revenue"         : 81.4,
            "net_income"      : 10.2,
            "operating_income": 13.7,
            "gross_profit"    : 17.5,
            "cash_flow"       : 14.9,
        },
        analysis = {
            "profit_margin"   : {"metric": "profit_margin",    "margin_%": 12.53},
            "operating_margin": {"metric": "operating_margin",  "margin_%": 16.83},
            "free_cash_flow"  : {"metric": "free_cash_flow",    "fcf": 6.0},
            "debt_to_equity"  : {"metric": "debt_to_equity",    "ratio": 0.25},
            "yoy_growth"      : {
                "revenue"    : {"growth_%": 8.53,  "insight": "Growth"},
                "net_income" : {"growth_%": 13.33, "insight": "Growth"},
            },
            "risk_flags"      : [],
        },
    )

    print(f"File : {result['file_path']}")
    print(f"\n{result['report']}")