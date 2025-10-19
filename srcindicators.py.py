# src/indicators.py
import numpy as np
import pandas as pd

def compute_basic_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "close" not in df.columns:
        candidates = [c for c in df.columns if "close" in c.lower()]
        if candidates:
            df["close"] = df[candidates[0]]
        else:
            raise ValueError("No 'close' column found.")
    df["sma_10"] = df["close"].rolling(10).mean()
    df["sma_50"] = df["close"].rolling(50).mean()
    df["sma_200"] = df["close"].rolling(200).mean()
    df["ema_20"] = df["close"].ewm(span=20).mean()
    delta = df["close"].diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.rolling(14).mean()
    roll_down = down.rolling(14).mean()
    rs = roll_up / roll_down
    df["rsi_14"] = 100 - (100 / (1 + rs))
    df["returns_1d"] = df["close"].pct_change()
    df["vol_30"] = df["returns_1d"].rolling(30).std() * np.sqrt(252)
    return df
