# src/data_client.py
import os
import time
import json
from pathlib import Path
from datetime import datetime, timedelta

import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv

load_dotenv()
ALPHAV_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", 1800))

def _cache_path(ticker: str, suffix: str = "timeseries.json") -> Path:
    return CACHE_DIR / f"{ticker.upper()}_{suffix}"

def _write_cache(path: Path, obj):
    path.write_text(json.dumps({"fetched_at": datetime.utcnow().isoformat(), "data": obj}))

def _load_cache(path: Path):
    raw = json.loads(path.read_text())
    fetched = datetime.fromisoformat(raw["fetched_at"])
    return fetched, raw["data"]

def fetch_time_series_alpha_vantage(ticker: str, outputsize: str = "compact") -> dict:
    if not ALPHAV_KEY:
        raise ValueError("ALPHAVANTAGE_API_KEY not set in .env")
    base = "https://www.alphavantage.co/query"
    params = {"function": "TIME_SERIES_DAILY_ADJUSTED", "symbol": ticker, "outputsize": outputsize, "apikey": ALPHAV_KEY}
    r = requests.get(base, params=params, timeout=30)
    r.raise_for_status()
    time.sleep(1.1)
    return r.json()

def cache_time_series(ticker: str, data: dict):
    p = _cache_path(ticker)
    _write_cache(p, data)

def load_cached_time_series(ticker: str):
    p = _cache_path(ticker)
    if not p.exists():
        return None
    fetched, data = _load_cache(p)
    if datetime.utcnow() - fetched > timedelta(seconds=CACHE_TTL):
        return None
    return data

def timeseries_json_to_df(alpha_json: dict) -> pd.DataFrame:
    key = None
    for k in alpha_json.keys():
        if "Time Series" in k:
            key = k
            break
    if key is None:
        raise ValueError("Unexpected AlphaV JSON structure")
    ts = alpha_json[key]
    df = pd.DataFrame.from_dict(ts, orient="index")
    df.index = pd.to_datetime(df.index)
    df.columns = [c.split(".")[-1].strip() for c in df.columns]
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df.sort_index(inplace=True)
    if "close" not in df.columns:
        candidates = [c for c in df.columns if "close" in c.lower()]
        if candidates:
            df["close"] = df[candidates[0]]
    # Keep only the columns we need
    return df

def get_time_series(ticker: str, use_cache_first=True, sample_fallback=True) -> pd.DataFrame:
    ticker = ticker.upper()
    if use_cache_first:
        cached = load_cached_time_series(ticker)
        if cached:
            try:
                return timeseries_json_to_df(cached)
            except Exception:
                pass
    if ALPHAV_KEY:
        try:
            j = fetch_time_series_alpha_vantage(ticker)
            cache_time_series(ticker, j)
            return timeseries_json_to_df(j)
        except Exception as exc:
            print(f"[data_client] AlphaV fetch failed: {exc}")
    # fallback: look for sample CSV
    sample = Path(f"data/sample_timeseries_{ticker}.csv")
    if sample.exists():
        df = pd.read_csv(sample, parse_dates=["date"], index_col="date").sort_index()
        if "close" not in df.columns and "Close" in df.columns:
            df["close"] = df["Close"]
        return df
    # generate synthetic data
    dates = pd.date_range(end=datetime.today(), periods=120)
    prices = 100 + np.cumsum(np.random.normal(0, 1.5, len(dates)))
    df = pd.DataFrame({"close": prices}, index=dates)
    return df
