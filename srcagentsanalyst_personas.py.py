# src/agents/analyst_personas.py
import os
import json
from dotenv import load_dotenv
load_dotenv()

USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if USE_OPENAI and OPENAI_KEY:
    import openai
    openai.api_key = OPENAI_KEY

def _simulated_analyst(persona: str, data: dict, news: dict) -> dict:
    price = data["last_close"]
    sentiment = news.get("sentiment_score_mean", 0)
    base = {
        "persona": persona,
        "thesis": f"{persona} sees mixed signals for {data['ticker']}.",
        "bullets": [],
        "risks": ["Macroeconomic slowdown", "Regulatory headwinds", "Competitive pressures"],
        "price_target": {"low": round(price * 0.8, 2), "median": round(price * 1.05, 2), "high": round(price * 1.35, 2)},
        "confidence": 60,
    }
    if "Growth" in persona:
        base["thesis"] = f"Growth analyst highlights product pipeline and revenue growth for {data['ticker']}."
        base["bullets"] = ["Strong product roadmap", "Rising revenue trends", "Positive sentiment recent quarters"]
        base["confidence"] = min(95, 60 + int(sentiment * 10))
    elif "Value" in persona:
        base["thesis"] = f"Value analyst focuses on valuation and cash flows for {data['ticker']}."
        base["bullets"] = ["Reasonable P/E vs peers", "Stable margins", "Healthy free cash flow"]
        base["confidence"] = 62
    else:
        base["thesis"] = f"Retail strategist emphasizes management quality and long-term durability for {data['ticker']}."
        base["bullets"] = ["Strong brand recognition", "Customer retention", "Operational improvement"]
        base["confidence"] = 58
    return base

def _openai_analyst(persona: str, data: dict, news: dict) -> dict:
    prompt = f"""
You are a financial analyst persona: {persona}.
Given the following facts (JSON), return a JSON object with keys: thesis, bullets (3 list), risks (3 list),
price_target (object with low, median, high), confidence (0-100).
Facts:
{json.dumps({'data': data, 'news': news}, default=str)}
Return only valid JSON.
"""
    resp = openai.ChatCompletion.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=500)
    text = resp["choices"][0]["message"]["content"]
    # crude: extract JSON substring
    import re
    m = re.search(r"(\{[\\s\\S]*\})", text)
    if not m:
        return _simulated_analyst(persona, data, news)
    try:
        return json.loads(m.group(1))
    except Exception:
        return _simulated_analyst(persona, data, news)

def run_analyst(persona: str, data: dict, news: dict) -> dict:
    if USE_OPENAI and OPENAI_KEY:
        return _openai_analyst(persona, data, news)
    return _simulated_analyst(persona, data, news)
