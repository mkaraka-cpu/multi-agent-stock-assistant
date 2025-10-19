# src/agents/evaluator.py
from typing import Dict, List

def score_analyst_output(analysis: Dict) -> Dict:
    issues = []
    score = 100
    if "price_target" not in analysis or not isinstance(analysis["price_target"], dict):
        issues.append("Missing price_target")
        score -= 40
    else:
        pt = analysis["price_target"]
        median = pt.get("median")
        if median is None:
            issues.append("Missing median price_target")
            score -= 30
    conf = analysis.get("confidence")
    if conf is None:
        issues.append("Missing confidence")
        score -= 20
    elif not (0 <= conf <= 100):
        issues.append("Confidence out of range")
        score -= 10
    if not analysis.get("thesis"):
        issues.append("Empty thesis")
        score -= 10
    if score < 0:
        score = 0
    return {"score": score, "issues": issues}

def evaluate_all(analyses: List[Dict]) -> Dict:
    results = []
    for a in analyses:
        s = score_analyst_output(a)
        results.append({"persona": a.get("persona", "unknown"), "score": s["score"], "issues": s["issues"]})
    avg = sum([r["score"] for r in results]) / len(results)
    return {"analyst_scores": results, "average_score": avg}

def optimize_if_needed(ticker: str, data_summary: dict, news_summary: dict, analyses: list, threshold: int = 60, max_attempts: int = 2):
    # Simple optimizer: re-run the persona if score below threshold, simulated behavior
    improved = []
    for a in analyses:
        s = score_analyst_output(a)["score"]
        attempts = 0
        cur = a
        while s < threshold and attempts < max_attempts:
            attempts += 1
            # in real system: refine prompt; here: call the analyst simulator again
            from src.agents.analyst_personas import _simulated_analyst
            cur = _simulated_analyst(a.get("persona", "Analyst"), data_summary, news_summary)
            s = score_analyst_output(cur)["score"]
        improved.append(cur)
    return improved
