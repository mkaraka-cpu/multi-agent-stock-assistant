# src/agents/data_agent.py
from typing import Dict
from src.data_client import get_time_series
from src.indicators import compute_basic_indicators

def data_agent_run(ticker: str) -> Dict:
    df = get_time_series(ticker)
    df_ind = compute_basic_indicators(df)
    latest = df_ind.iloc[-1]
    summary = {
        "ticker": ticker,
        "last_close": float(latest["close"]),
        "sma_10": float(latest.get("sma_10", float("nan"))),
        "sma_50": float(latest.get("sma_50", float("nan"))),
        "sma_200": float(latest.get("sma_200", float("nan"))),
        "ema_20": float(latest.get("ema_20", float("nan"))),
        "rsi_14": float(latest.get("rsi_14", float("nan"))),
        "macd": float(latest.get("macd", float("nan"))) if "macd" in latest.index else None,
        "vol_30": float(latest.get("vol_30", float("nan"))),
        "history": df_ind.tail(120).reset_index().rename(columns={"index": "date"}).to_dict(orient="records"),
    }
    return summary
