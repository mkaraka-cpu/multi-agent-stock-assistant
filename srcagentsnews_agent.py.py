# src/agents/news_agent.py
from typing import Dict, List
from src.sentiment import score_headlines

def fetch_news_headlines_simulated(ticker: str, max_headlines: int = 8) -> List[str]:
    examples = [
        f"{ticker} beats quarterly revenue expectations",
        f"{ticker} announces new product roadmap",
        f"Analysts mixed on {ticker}'s near-term growth",
        f"{ticker} faces regulatory scrutiny overseas",
        f"{ticker} expands in emerging markets",
        f"{ticker} reports improved margins this quarter",
        f"{ticker} delays product launch amid supply issues",
        f"{ticker} to increase R&D spending next year"
    ]
    return examples[:max_headlines]

def news_agent_run(ticker: str) -> Dict:
    headlines = fetch_news_headlines_simulated(ticker, max_headlines=8)
    scored = score_headlines(headlines)
    agg = {"positive": 0, "neutral": 0, "negative": 0}
    for s in scored:
        agg[s["label"]] += 1
    summary = {
        "headlines": scored,
        "sentiment_counts": agg,
        "sentiment_score_mean": sum([h["compound"] for h in scored]) / len(scored),
    }
    return summary
