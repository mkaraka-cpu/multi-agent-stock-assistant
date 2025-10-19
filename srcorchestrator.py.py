# src/orchestrator.py
from typing import List, Dict
from src.agents.data_agent import data_agent_run
from src.agents.news_agent import news_agent_run
from src.agents.analyst_personas import run_analyst
from src.agents.evaluator import evaluate_all, optimize_if_needed
from pathlib import Path
import json

MEMORY_PATH = Path("data/memory.json")

def load_memory():
    if MEMORY_PATH.exists():
        return json.loads(MEMORY_PATH.read_text())
    return {"history": []}

def append_memory(entry: dict):
    mem = load_memory()
    mem["history"].append({"timestamp": __import__("datetime").datetime.utcnow().isoformat(), **entry})
    mem["history"] = mem["history"][-50:]
    MEMORY_PATH.write_text(json.dumps(mem, indent=2))

def synthesize_report(ticker: str, data_summary: dict, news_summary: dict, analyses: List[dict]) -> dict:
    weighted_sum = 0.0
    weight_total = 0.0
    medians = []
    confidences = []
    for a in analyses:
        pt = a.get("price_target", {})
        median = pt.get("median")
        conf = a.get("confidence", 50)
        if median is None:
            continue
        weighted_sum += median * (conf / 100)
        weight_total += (conf / 100)
        medians.append(median)
        confidences.append(conf)
    final_price = (weighted_sum / weight_total) if weight_total > 0 else None
    last = data_summary["last_close"]
    rec = "HOLD"
    if final_price is not None:
        if final_price >= last * 1.15:
            rec = "BUY"
        elif final_price <= last * 0.9:
            rec = "SELL"
        else:
            rec = "HOLD"
    return {"ticker": ticker, "last_close": last, "aggregated_price_target": final_price, "recommendation": rec, "analyst_medians": medians, "analyst_confidences": confidences}

def run_full_workflow(ticker: str, optimize: bool = True) -> Dict:
    print(f"[orchestrator] Starting workflow for {ticker}")
    # 1. Plan & fetch data (Prompt Chaining start)
    data_summary = data_agent_run(ticker)
    news_summary = news_agent_run(ticker)
    # 2. Routing: choose personas
    personas = ["Growth & Technology Analyst", "Value Analyst", "Retail & Long-Term Strategist"]
    analyses = []
    for p in personas:
        a = run_analyst(p, data_summary, news_summary)
        a["persona"] = p
        analyses.append(a)
    # 3. Evaluate
    eval_before = evaluate_all(analyses)
    print("Evaluation before optimization:", eval_before)
    # 4. Optimizer -> refine low scored analyses
    if optimize:
        analyses = optimize_if_needed(ticker, data_summary, news_summary, analyses)
    eval_after = evaluate_all(analyses)
    print("Evaluation after optimization:", eval_after)
    # 5. Synthesize final
    final = synthesize_report(ticker, data_summary, news_summary, analyses)
    # 6. Self-reflect: store memory
    append_memory({"ticker": ticker, "final_price": final["aggregated_price_target"], "recommendation": final["recommendation"], "eval_score": eval_after["average_score"]})
    report = {"data": data_summary, "news": news_summary, "analyses": analyses, "evaluation_before": eval_before, "evaluation_after": eval_after, "final": final}
    return report

def pretty_print_report(report: Dict):
    print("\n=== Synthesized Report ===")
    f = report["final"]
    print(f"Ticker: {f['ticker']}")
    print(f"Last Close: {f['last_close']:.2f}")
    if f["aggregated_price_target"] is not None:
        print(f"Aggregated price target: {f['aggregated_price_target']:.2f}")
    print(f"Recommendation: {f['recommendation']}")
    print("\nAnalyst outputs:")
    for a in report["analyses"]:
        print(f"--- {a.get('persona')}")
        print(f"Thesis: {a.get('thesis')}")
        print(f"Price target (median): {a.get('price_target', {}).get('median')}")
        print(f"Confidence: {a.get('confidence')}")
    print("\nEvaluation summary:", report.get("evaluation_after", {}))
