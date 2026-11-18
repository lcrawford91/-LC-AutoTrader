# LC AutoTrader AI — Paper Bot v1

This is the first working foundation for an AI-assisted Coinbase **paper-trading** system. **It cannot place live orders, withdraw funds, or sign transactions.**

## What is implemented
- Coinbase public market candle reader (read-only; Exchange market-data endpoint).
- EMA/RSI/volume-driven quick-trade signal generation on closed 1m and 5m candles.
- Decimal-based virtual GBP spot wallet with fees, spread and slippage.
- One-position and reserve rules, cost-aware entry checks, protective stop and target.
- SQLite learning journal recording decisions, outcomes and error classifications.
- Read-only Advanced Trade account connector (requires your own server-side portfolio-scoped view key).
- FastAPI health, scan and paper-cycle endpoints; no trade/write API.
- Automated offline tests in GitHub Actions.

## Security
No live order execution implementation exists in this release. Trading, transfers and withdrawals are **permanently disabled** in this branch. Never put Coinbase keys in this repository, a browser, or messages to Grok/ChatGPT. Only add view-only keys to an approved secrets manager when private backend hosting is ready. The sample env file contains no secrets.

## Development environment
Python 3.11+; dependencies are in requirements.txt.
- Start the API using `uvicorn app.api:app --app-dir ai-paper-bot --host 127.0.0.1 --port 8000` from the repository root after installing requirements.
- Or change into this folder and use `uvicorn app.api:app`.
- The `/api/scan/{product_id}` endpoint reads current closed candles and returns a signal only.
- The `/api/paper-cycle/{product_id}` endpoint simulates a trade decision in memory; repeated calls can open/close a virtual position. **Do not expose this prototype publicly**: it has no user authentication and uses ephemeral in-memory balances.
- The API's `/api/portfolio` returns only virtual portfolio information.
- `/api/account-status` reports whether read-only credentials are configured; it never returns secrets.

## Limitations
This is a **starter**, not a deployable 24/7 live bot. It has no autonomous background worker yet; paper cycles are requested explicitly via API. Market-data latency and liquidity are not exchange-execution quality; the paper fills are simplified. Advanced Trade authenticated account connectivity has not been tested with a real account. No AI model autonomously edits strategy code: the learning journal records patterns and proposed experiments, which must be validated independently. Real-time WebSocket feeds, full-market discovery, authentication, persistent paper portfolio state and production deployment are next milestones.

## Next build phases
1. Protected worker with WebSocket feeds, full Coinbase eligible-product discovery, monitoring and persistent virtual wallet.
2. User-authenticated web dashboard with charts, order lists and backtesting.
3. Automated walk-forward experiments, shadow-paper evaluation and rollback.
4. Secure read-only Advanced connection. Live gateway remains a separate project and disabled until independently reviewed.

**No profit guarantees. Backtests and paper results are not live returns.**
