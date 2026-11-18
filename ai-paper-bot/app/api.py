"""Prototype FastAPI paper dashboard endpoints. Never expose publicly without auth."""
from __future__ import annotations
from decimal import Decimal
import os
from fastapi import FastAPI, HTTPException
from .coinbase_readonly import credential_status
from .market import public_candles, validate_product
from .strategy import quick_signal
from .paper import PaperBroker
from .learning import LearningJournal

app = FastAPI(title="LC AutoTrader AI — PAPER ONLY", version="0.1.0")
broker = PaperBroker(starting_gbp=os.getenv("PAPER_STARTING_GBP","1000"),
                     max_trade_gbp=os.getenv("PAPER_MAX_TRADE_GBP","25"),
                     cash_reserve=os.getenv("PAPER_CASH_RESERVE_GBP","5"))
journal = LearningJournal()

@app.get("/api/status")
def status():
    return {"service": "LC AutoTrader AI", "mode": "PAPER",
            "live_trading_enabled": False, "orders_enabled": False, "coinbase": credential_status()}

@app.get("/api/portfolio")
def portfolio():
    return broker.snapshot()

@app.get("/api/orders")
def orders():
    return {"mode": "PAPER", "orders": broker.events[-100:]}

@app.get("/api/learning")
def learning():
    return journal.observations()

@app.get("/api/scan/{product_id}")
def scan(product_id: str, seconds: int = 300):
    try:
        validate_product(product_id)
        if seconds not in (60, 300):
            raise ValueError("Supported quick-trade intervals: 60, 300 seconds")
        candles = public_candles(product_id, granularity=seconds)
        signal = quick_signal(candles)
        return {**{k:str(v) if isinstance(v,Decimal) else v for k,v in vars(signal).items()},
                "mode": "PAPER", "product": product_id.upper(), "closed_candles": len(candles)}
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.post("/api/paper-cycle/{product_id}")
def paper_cycle(product_id: str, seconds: int = 300):
    # Prototype is not authenticated or durable; this mutates VIRTUAL balances only.
    result = scan(product_id, seconds)
    product = result["product"]
    price = Decimal(result["price"])
    event = broker.exit_check(product, price)
    if event is None and result["side"] == "BUY" and broker.position is None:
        try:
            event = broker.buy(product, price)
        except ValueError as exc:
            event = {"side": "REJECTED", "reason": str(exc), "mode": "PAPER"}
    journal.record("momentum-v1", product, result, result["reason"])
    return {"signal": result, "paper_event": event, "paper_wallet": broker.snapshot(price)}
