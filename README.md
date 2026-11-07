# Strategy learning boundary

The system can improve its signals without giving the learning component authority to place trades or edit live risk settings.

## What it learns from

- Completed candles and their timestamps, with data gaps and stale quotes recorded.
- Strategy signals, risk-preview decisions, skipped orders and reasons.
- Reconciled fills, fees, spread/slippage estimates, cancels and stop events.
- Market/product availability and strategy version at the time of each event.

Do not use account passwords or secrets as model inputs. Keep audit data local to the backend or the user's audit store; do not send balances/orders to third-party analytics.

## Evaluation flow

1. Freeze a versioned dataset and strategy definition.
2. Generate candidate parameter sets in offline research.
3. Backtest only on completed candles with no look-ahead, fee/slippage modeling, warmup rules, and chronological train/validation/out-of-sample splits.
4. Track net results plus drawdown, exposure, trade count, turnover, concentration and cost sensitivity.
5. Forward/shadow-check shortlisted candidates in a physically separate evaluation ledger; never mix simulated positions or cash with live portfolio views.
6. Require review of candidate version and evidence before promotion; keep the prior version available for immediate rollback.

## Hard limits

Learning cannot change the order cap, daily-loss cutoff, protected BTC floor, product/venue allowlist, order type, leverage/short restrictions, automation enable state, or kill-switch. It cannot invoke the order adapter. Live strategy configuration is immutable during a run; a new version takes effect only after a separately reviewed promotion and reconciliation.

Never promote based on a single profitable trade or training-set return alone. If data, fees, quote freshness, or evaluation evidence are incomplete, keep the current strategy and mark the candidate unqualified.
