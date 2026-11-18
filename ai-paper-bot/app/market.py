"""Public Coinbase market data; no account permissions or trading methods."""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
import json
import time
import urllib.error
import urllib.parse
import urllib.request

ALLOWED_GRANULARITIES = {60, 300, 900, 3600, 21600, 86400}
BASE = "https://api.exchange.coinbase.com"
MAX_CANDLES = 300

@dataclass(frozen=True)
class Candle:
    timestamp: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

def validate_product(product_id: str) -> str:
    # Explicitly restrict symbols for the first paper-only prototype.
    if not (5 <= len(product_id) <= 24 and product_id.replace("-", "").isalnum() and "-" in product_id):
        raise ValueError("Invalid product ID")
    return product_id.upper()

def public_candles(product_id: str, granularity: int = 300) -> list[Candle]:
    product_id = validate_product(product_id)
    if granularity not in ALLOWED_GRANULARITIES:
        raise ValueError("Unsupported candle interval")
    # Pull historical CLOSED candles. Coinbase Exchange endpoint is public market data,
    # not the authenticated Coinbase Advanced trading endpoint.
    cutoff = int(time.time() // granularity * granularity)
    url = BASE + "/products/" + urllib.parse.quote(product_id) + "/candles?" + urllib.parse.urlencode(
        {"granularity": granularity}
    )
    request = urllib.request.Request(url, headers={"User-Agent": "LC-AutoTrader-AI-Paper/1.0", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            raw = json.load(response)
    except (OSError, ValueError, urllib.error.HTTPError) as exc:
        raise RuntimeError("Unable to retrieve Coinbase public candles") from exc
    if not isinstance(raw, list):
        raise RuntimeError("Unexpected market data format")
    candles = []
    for row in raw[:MAX_CANDLES]:
        if not (isinstance(row, list) and len(row) >= 6):
            continue
        timestamp = int(row[0])
        if timestamp >= cutoff:
            continue  # exclude current incomplete candle
        candles.append(Candle(timestamp, Decimal(str(row[3])), Decimal(str(row[2])),
                              Decimal(str(row[1])), Decimal(str(row[4])), Decimal(str(row[5]))))
    candles.sort(key=lambda c: c.timestamp)
    return candles

def quote_currency(product_id: str) -> str:
    return validate_product(product_id).split("-")[-1]
