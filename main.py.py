"""
Main entrypoint for Multi-Agent Stock Research Assistant.
Usage:
    python main.py <TICKER>
"""
import sys
import json
from pathlib import Path

# ensure src is importable
from src.orchestrator import run_full_workflow, pretty_print_report

Path("data/cache").mkdir(parents=True, exist_ok=True)
Path("output").mkdir(parents=True, exist_ok=True)

def main(argv):
    if len(argv) < 2:
        print("Usage: python main.py <TICKER>")
        return
    ticker = argv[1].upper()
    report = run_full_workflow(ticker)
    pretty_print_report(report)
    out_p = Path("output") / f"{ticker}_report.json"
    out_p.write_text(json.dumps(report, indent=2, default=str))
    print(f"\nReport saved to {out_p}")

if __name__ == "__main__":
    main(sys.argv)
