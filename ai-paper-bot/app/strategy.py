"""Deterministic indicators and cost-conscious paper trade signals."""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from .market import Candle

@dataclass(frozen=True)
class Signal:
    side: str
    reason: str
    price: Decimal
    rsi: Decimal
    ema_fast: Decimal
    ema_slow: Decimal
    relative_volume: Decimal
    timestamp: int

def ema(values: list[Decimal], span: int) -> Decimal:
    if len(values) < span:
        raise ValueError("Insufficient EMA observations")
    alpha = Decimal(2) / Decimal(span + 1)
    value = sum(values[:span], Decimal(0)) / Decimal(span)
    for sample in values[span:]:
        value = alpha * sample + (Decimal(1) - alpha) * value
    return value

def rsi(values: list[Decimal], period: int = 14) -> Decimal:
    if len(values) <= period:
        raise ValueError("Insufficient RSI observations")
    deltas = [b-a for a,b in zip(values[:-1], values[1:])]
    gains = [max(d, Decimal(0)) for d in deltas[-period:]]
    losses = [max(-d, Decimal(0)) for d in deltas[-period:]]
    average_gain = sum(gains, Decimal(0))/period
    average_loss = sum(losses, Decimal(0))/period
    if average_gain == 0 and average_loss == 0:
        return Decimal(50)
    if average_loss == 0:
        return Decimal(100)
    return Decimal(100) - Decimal(100)/(Decimal(1) + average_gain/average_loss)

def quick_signal(candles: list[Candle]) -> Signal:
    if len(candles) < 35:
        raise ValueError("Need at least 35 closed candles")
    data = sorted(candles, key=lambda c: c.timestamp)
    if len({c.timestamp for c in data[-35:]}) != 35:
        raise ValueError("Duplicate candle timestamps")
    closes = [c.close for c in data]
    if any(c <= 0 for c in closes):
        raise ValueError("Nonpositive market price")
    fast, slow = ema(closes, 9), ema(closes, 21)
    relative_volume = (data[-1].volume / (sum((c.volume for c in data[-21:-1]), Decimal(0))/20)
                       if sum((c.volume for c in data[-21:-1]), Decimal(0)) > 0 else Decimal(0))
    oscillator = rsi(closes)
    breakout = data[-1].close > max(c.high for c in data[-11:-1])
    qualifying = fast > slow and Decimal(55) <= oscillator <= Decimal(70) and relative_volume >= Decimal("1.5") and breakout
    return Signal("BUY" if qualifying else "WAIT", "momentum breakout confirmed" if qualifying
                  else "criteria not met", closes[-1], oscillator, fast, slow, relative_volume, data[-1].timestamp)
