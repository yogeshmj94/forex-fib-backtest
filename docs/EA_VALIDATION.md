# EA implementation and parity plan

## Frozen reference

The EA must reproduce the Python reference strategy before demo or live trading.

- 20 FX pairs
- 3-pip stop buffer
- fixed 1R take profit
- 0.20% of initial account balance risk per trade
- no compounding
- maximum observed/research portfolio guard: 8 strategy positions / 1.60% nominal open risk
- entry, order-block, session and multi-timeframe rules must remain identical to the Python engine

## Safety rule

`ea/ForexFibEA.mq5` starts with `EnableTrading=false`. Version 0.1 implements the execution/risk shell only. It deliberately does **not** create autonomous signals yet. This prevents an incomplete MQL translation from silently trading something different from the validated Python strategy.

## Reconciliation gate

Before enabling autonomous entries:

1. Export deterministic Python reference fixtures containing symbol, direction, setup timestamp, fill/expiry timestamp, entry, structural stop, buffered stop, TP and outcome.
2. Implement the MQL5 signal detector against the same frozen candles.
3. Compare MQL output to Python fixtures at event level, not only portfolio P&L.
4. Require exact agreement on setup direction and timestamps and tolerance-based agreement on prices.
5. Investigate every mismatch. Do not “tune” MQL rules to improve returns.
6. Only after parity passes, connect the signal detector to `PlaceFrozenOrder()`.
7. Compile in MetaEditor and run on MT5 demo with trading initially disabled; inspect logs and calculated lot sizes.
8. Enable demo trading only after execution checks pass.

## Risk implementation

Position size is calculated from a fixed reference balance, not current equity. If `InitialAccountBalance` is set, that value remains the risk base. At 0.20%, each full-stop loss is intended to equal 0.20% of that initial balance, subject to broker volume-step rounding and symbol tick-value metadata.

The EA computes pip size as 0.0001 for standard 5-digit non-JPY FX quotes and 0.01 for standard 3-digit JPY quotes by converting 10 broker points to one pip.

## What is not yet implemented

- frozen H4 setup detector
- multi-timeframe OB search/selection
- London/NY session gating
- pending-order expiry/invalidation
- exact live-candle chronology rules
- restart/state recovery
- daily prop-firm equity-loss guard
- broker/prop-specific symbol suffix handling

These are intentionally outstanding rather than guessed. The Python engine remains the source of truth.

## Running the MQL parity harness

1. Generate `reference_trades.jsonl` with `python -m src.export_parity --trades <validated trades.csv>`.
2. Copy the JSONL file into the MT5 terminal Files directory used by the Strategy Tester/script.
3. Compile `ForexFibEA.mq5` and `ParityHarness.mq5` in MetaEditor.
4. Run `ParityHarness` with the same broker symbols/history.
5. Treat every `PARITY FAIL` as an implementation discrepancy. Autonomous trading remains disabled until setup, OB, and applicable lifecycle checks pass.

The harness compares direction, H4/Fib construction, OB existence/entry and lifecycle outcome. Price comparisons use broker points as a small tolerance because broker OHLC representations can differ at the final decimal.
