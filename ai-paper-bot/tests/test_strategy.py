from decimal import Decimal
import pytest
from app.market import Candle
from app.strategy import ema, rsi, quick_signal
from app.learning import LearningJournal
from app.coinbase_readonly import credential_status

def test_indicators_and_signal_on_closed_candles():
    data=[Candle(i*300, Decimal("100"), Decimal("102"), Decimal("99"), Decimal("100")+Decimal(i)/10, Decimal("1")) for i in range(40)]
    result=quick_signal(data)
    assert result.side in ("BUY","WAIT")
    assert result.timestamp==39*300
    assert Decimal(0)<=result.rsi<=Decimal(100)

def test_not_enough_data():
    with pytest.raises(ValueError):
        quick_signal([])

def test_learning_never_self_promotes():
    j=LearningJournal()
    i=j.record("momentum-v1","BTC-GBP",{"side":"WAIT"},"not enough volume")
    j.outcome(i,"-0.24","fees")
    report=j.observations()
    assert report["classified_errors"]["fees"]==1
    assert report["automatic_strategy_promotion"] is False

def test_readonly_connector_unconfigured(monkeypatch):
    monkeypatch.delenv("COINBASE_API_KEY_NAME",raising=False)
    monkeypatch.delenv("COINBASE_API_PRIVATE_KEY",raising=False)
    assert credential_status()["configured"] is False
    assert credential_status()["live_trading_enabled"] is False
