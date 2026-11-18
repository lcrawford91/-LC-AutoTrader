"""Write-ahead decision journal and testable improvement proposals (no self-modifying code)."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path

class LearningJournal:
    def __init__(self, path: str = ":memory:"):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.execute("""CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            strategy_version TEXT NOT NULL, product TEXT NOT NULL, signal TEXT NOT NULL,
            reasons TEXT NOT NULL, outcome_pnl TEXT, error_type TEXT)""")
        self.db.commit()

    def record(self, strategy_version: str, product: str, signal: dict, reason: str) -> int:
        cursor = self.db.execute(
            "INSERT INTO decisions(strategy_version, product, signal, reasons) VALUES(?,?,?,?)",
            (strategy_version, product, json.dumps(signal), reason))
        self.db.commit()
        return int(cursor.lastrowid)

    def outcome(self, decision_id: int, pnl: str, error_type: str = "") -> None:
        if error_type not in ("", "poor_entry", "premature_exit", "late_exit", "fees", "regime", "unknown"):
            raise ValueError("Unknown mistake classification")
        cur = self.db.execute("UPDATE decisions SET outcome_pnl=?, error_type=? WHERE id=?",
                              (pnl, error_type, decision_id))
        self.db.commit()
        if cur.rowcount != 1:
            raise KeyError("Unknown decision")

    def observations(self) -> dict:
        rows = self.db.execute("SELECT error_type, COUNT(*) FROM decisions WHERE error_type IS NOT NULL AND error_type <> '' GROUP BY error_type").fetchall()
        suggestions = {"fees": "Test stricter spread and net-edge filters",
                       "poor_entry": "Test later candle confirmation",
                       "premature_exit": "Test volatility-adjusted exit rules",
                       "late_exit": "Test quicker trend invalidation",
                       "regime": "Test market regime filters",
                       "unknown": "Gather more tagged examples"}
        return {"classified_errors": dict(rows),
                "candidate_experiments": [suggestions[k] for k,_ in rows if k in suggestions],
                "automatic_strategy_promotion": False}
