from decimal import Decimal
import pytest
from app.paper import PaperBroker

def test_round_trip_always_accounts_for_fees_and_slippage():
    b = PaperBroker("1000","25","5")
    buy = b.buy("BTC-GBP", Decimal("100"))
    assert Decimal(buy["spent"]) <= Decimal("25")
    assert b.cash >= Decimal("975")
    sell = b.sell(Decimal("100"), "manual")
    assert Decimal(sell["pnl"]) < 0
    assert b.position is None
    assert b.cash < Decimal("1000")

def test_no_overspend_or_second_position():
    b = PaperBroker("20","25","5")
    with pytest.raises(ValueError):
        b.buy("BTC-GBP", Decimal("100"))
    b.buy("BTC-GBP",Decimal("100"),Decimal("10"))
    with pytest.raises(ValueError):
        b.buy("BTC-GBP",Decimal("100"),Decimal("10"))

def test_no_non_gbp_paper_orders():
    b = PaperBroker()
    with pytest.raises(ValueError):
        b.buy("ETH-USD",Decimal("2000"))

def test_profit_target_and_stop_are_simulated():
    b=PaperBroker()
    b.buy("BTC-GBP",Decimal("100"))
    assert b.exit_check("BTC-GBP",Decimal("101")) is None
    assert b.exit_check("BTC-GBP",Decimal("104"))["reason"]=="profit_target"
    assert b.position is None
