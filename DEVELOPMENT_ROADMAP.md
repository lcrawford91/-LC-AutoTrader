# LC AutoTrader Live APK — phased build plan

## Current starting point

The latest supplied `LC-AutoTrader-Android-main.zip` contains only a FastAPI paper simulator (`app.py`), a short README, and an APK workflow YAML. It has no Android Gradle project, no Coinbase Advanced live adapter, no eToro adapter, and no APK output. The simulator uses public Coinbase Exchange quotes and assumed fees; it is not linked to either user's live account. Keep it isolated and do not relabel its paper endpoints as live.

## Phase 0 — Resolve access and product decisions

- Confirm which source repository/package is authoritative before merging this scaffold.
- Verify Coinbase Advanced Trade account/API permissions and whether the existing desk connection can be delegated to a separate app/backend.
- Verify eToro API key eligibility, available permissions, UK instruments, API terms, live/demo separation, and order support. The current public developer material describes API key headers (`x-api-key`, `x-user-key`) and live/demo order paths; it does not establish that an existing desk link is reusable by an APK.
- Resolve sizing conflict: this brief proposes ~£375 per scalp, while the previously confirmed LC AutoTrader cap is £10 per order. Current scaffold keeps £10 as the active ceiling, with live execution disabled. Set any higher cap only after a separate reviewed configuration change.
- Verify the BTC floor against live account holdings before activation. The provided baseline implies a minimum retained balance of 0.00067657 BTC (0.00135313 − 0.00067656).

**Exit gate:** documented account/API access, allowed product universe, approved order cap, portfolio exposure cap, and runtime ownership.

## Phase 1 — Native app and secure control plane

- Build a Kotlin Android app with Material 3, biometric app lock, account/market/portfolio screens, charts, order views, and notifications.
- Use Android Keystore-backed local session protection. Do not embed provider API secrets in the APK.
- Add an authenticated HTTPS control API and persistent execution service. Keep provider credentials server-side with minimum permissions and no withdrawal access. The phone remains a control/monitoring client; do not promise 24/7 execution from a background phone process.
- Add Coinbase and eToro adapters behind a common venue interface. Report unsupported markets as unavailable; never map to a substitute pair.

**Exit gate:** real read-only portfolio data reconciles with each venue, while order submission remains disabled.

## Phase 2 — Risk engine and manual order lifecycle

- Implement server-side risk checks using decimal arithmetic: spot-only, no leverage/short/CFD, £10 maximum order including fees, £3 daily loss latch, reserved cash, BTC protected floor, stale-data and unsupported-product blocks.
- Require a fresh venue preview, fee estimate, order-size rounding/minimum checks, risk decision, persisted intent, and unique idempotency/client order ID before create.
- On timeout, reconcile by client ID/order history/fills before any retry. Handle partial fills, cancel races, reservations and audit transitions.
- Add manual limit orders first, then only order types each venue confirms it supports. Every order is previewed; manual confirm remains explicit.

**Exit gate:** mocked order-path and risk cases pass; no real orders used for verification.

## Phase 3 — Portfolio, charts, alerts and exports

- Add live balances, GBP/USD valuation, free cash, holdings, open orders, unrealized P&L, searchable markets and historical candles.
- Add strategy/order markers, watchlists, price alerts, notifications, audit history and UK CGT CSV export.
- Reconcile every displayed order/fill/fee with provider records; mark missing/stale data.

**Exit gate:** account and order records reconcile for both providers and unsupported assets display clearly.

## Phase 4 — Automation, kill-switch and operational hardening

- Define each strategy precisely: completed-candle timestamp, indicator warmup, quote freshness, spread ceiling, relative-volume calculation, entry/exit rules, fee/slippage model and position ownership.
- Require preview → risk approval → idempotent place; automation state and persistent kill-switch checked again immediately before create.
- Kill-switch blocks all new strategy orders, persists across restart, reports health/heartbeat, and permits only explicitly authorized risk-reducing actions.
- Add bounded retries, audit signal → preview → order → fill, alerts on partial/fill/reject/cancel/stop/funding issue, and reconciliation after restart.

**Exit gate:** end-to-end demo/mock workflows and operational recovery pass; automation still off by default.

## Phase 5 — Strategy learning and controlled improvement

- Keep a versioned research journal of completed-candle inputs, signals, previews, orders, fills, fees, slippage, skips and missed setups.
- Evaluate candidate parameter changes offline against historical data with realistic fees/slippage, no look-ahead, and separate in-sample, validation and out-of-sample periods. Keep any paper/evaluation ledger separate from live balances and live P&L.
- Compare candidates using net returns alongside drawdown, exposure, trade count, turnover, and fee sensitivity; reject strategies that only improve the training period or rely on stale/missing data.
- Promote a candidate only after a minimum forward/shadow period and an explicit review of its version, products, sizing, stop rules and measured results. Preserve rollback to the prior strategy.
- Do not allow learning to raise risk caps, lower the BTC floor, disable the kill-switch, change venue/product scope, or start live orders. Live configuration changes remain separately authorized.

**Exit gate:** candidate evaluation is reproducible, experiments remain isolated, promotion/rollback is audited, and learning cannot bypass the execution risk engine.

## Phase 6 — APK and release handoff

- Pin supported Android/Gradle/SDK versions in the repository and repair GitHub Actions to build debug and signed release variants.
- Store signing credentials only in protected CI secrets; produce artifact checksums and a release checklist.
- Verify package identity, min SDK, permissions, install/launch on Android, account linking, order display, kill-switch behavior and uninstall/signing upgrade path.
- Publish installation and day-to-day instructions only after the APK and tests are available.

**Exit gate:** verified debug APK, signed release APK, README, test evidence, and a separate reviewed live activation summary.

## Release blockers / unknowns

- Whether Coinbase/eToro account links in this desk grant app/API access: unknown.
- Provider credentials, permissions, supported account types, product availability and fees: unknown until verified through official account/API surfaces.
- £375 scalp vs £10 active cap: unresolved; scaffold retains £10.
- Exact strategy, portfolio-wide exposure cap, runtime host and signing owner: to be decided before live activation.
- Learning promotion thresholds and minimum forward/shadow duration: to be specified before strategy promotion.
