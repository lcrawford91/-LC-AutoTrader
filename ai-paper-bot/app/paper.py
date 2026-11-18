"""Pure paper brokerage. Not connected to any live order API."""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal

D = Decimal

@dataclass
class Position:
    product: str
    quantity: Decimal
    entry_price: Decimal
    entry_cost: Decimal
    stop: Decimal
    target: Decimal

class PaperBroker:
    def __init__(self, starting_gbp="1000", max_trade_gbp="25", cash_reserve="5",
                 fee_rate="0.006", half_spread="0.0005", slippage="0.0005"):
        self.cash = D(str(starting_gbp))
        self.max_trade = D(str(max_trade_gbp))
        self.reserve = D(str(cash_reserve))
        self.fee = D(str(fee_rate))
        self.half_spread = D(str(half_spread))
        self.slippage = D(str(slippage))
        if self.cash <= 0 or self.max_trade <= 0 or self.reserve < 0:
            raise ValueError("Invalid balance or limits")
        if any(not D(0) <= value < D("0.1") for value in (self.fee, self.half_spread, self.slippage)):
            raise ValueError("Invalid simulated cost parameters")
        self.position: Position | None = None
        self.events = []

    def buy(self, product: str, mid: Decimal, budget: Decimal | None = None) -> dict:
        if self.position:
            raise ValueError("Only one simulated position at a time")
        if not product.endswith("-GBP"):
            raise ValueError("GBP paper balance only supports GBP quoted spot pairs")
        if mid <= 0:
            raise ValueError("Price must be positive")
        budget = self.max_trade if budget is None else D(str(budget))
        if budget <= 0 or budget > self.max_trade or budget > self.cash - self.reserve:
            raise ValueError("Paper trade exceeds limits or cash reserve")
        fill = mid * (D(1) + self.half_spread + self.slippage)
        quantity = budget / (fill * (D(1) + self.fee))
        fee = quantity * fill * self.fee
        spent = quantity * fill + fee
        self.cash -= spent
        self.position = Position(product, quantity, fill, spent, fill * D("0.99"), fill * D("1.02"))
        event = {"side": "BUY", "product": product, "quantity": str(quantity),
                 "price": str(fill), "fee": str(fee), "spent": str(spent), "mode": "PAPER"}
        self.events.append(event)
        return event

    def sell(self, mid: Decimal, reason: str) -> dict:
        if not self.position:
            raise ValueError("No simulated position")
        if mid <= 0:
            raise ValueError("Price must be positive")
        pos = self.position
        fill = mid * (D(1) - self.half_spread - self.slippage)
        gross = pos.quantity * fill
        fee = gross * self.fee
        net = gross - fee
        pnl = net - pos.entry_cost
        self.cash += net
        self.position = None
        event = {"side": "SELL", "product": pos.product, "quantity": str(pos.quantity),
                 "price": str(fill), "fee": str(fee), "net": str(net), "pnl": str(pnl),
                 "reason": reason, "mode": "PAPER"}
        self.events.append(event)
        return event

    def exit_check(self, product: str, mid: Decimal) -> dict | None:
        pos = self.position
        if not pos or pos.product != product:
            return None
        if mid <= pos.stop:
            return self.sell(mid, "stop_loss")
        if mid >= pos.target:
            return self.sell(mid, "profit_target")
        return None

    def snapshot(self, market_price: Decimal | None = None) -> dict:
        exposure = D(0)
        if self.position and market_price is not None:
            exposure = self.position.quantity * market_price
        return {"mode": "PAPER", "cash_gbp": str(self.cash),
                "estimated_equity_gbp": str(self.cash + exposure),
                "position": None if not self.position else {
                    "product": self.position.product, "quantity": str(self.position.quantity),
                    "entry_price": str(self.position.entry_price),
                    "stop": str(self.position.stop), "target": str(self.position.target)},
                "trades": len(self.events), "live_trading_enabled": False}
