from __future__ import annotations

import pandas as pd


def ema_signal(
    candles: pd.DataFrame,
    fast_period: int = 9,
    slow_period: int = 21,
    price_column: str = "close",
) -> str:
    if fast_period >= slow_period:
        raise ValueError("fast_period must be lower than slow_period")
    if len(candles) < slow_period + 2:
        return "HOLD"

    prices = candles[price_column]
    fast = prices.ewm(span=fast_period, adjust=False).mean()
    slow = prices.ewm(span=slow_period, adjust=False).mean()

    previous_fast, current_fast = fast.iloc[-2], fast.iloc[-1]
    previous_slow, current_slow = slow.iloc[-2], slow.iloc[-1]

    if previous_fast <= previous_slow and current_fast > current_slow:
        return "BUY"
    if previous_fast >= previous_slow and current_fast < current_slow:
        return "SELL"
    return "HOLD"
