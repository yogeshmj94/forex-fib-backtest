# Forex Fib Backtest

Backtester for the 20-pair H4 scanner strategy.

## Locked rules
- H4 setup; Live-1 must close beyond Live-2 high (bullish) or low (bearish).
- Fib range: Live-2 extreme to Live-1 extreme.
- Entry is a limit at the 0.60 retracement.
- Entry is valid only during the immediately following H4 candle (Live). If unfilled by its close, setup expires.
- Bullish SL: Live-2 low - 5 pips. TP: Live-1 high.
- Bearish SL: Live-2 high + 5 pips. TP: Live-1 low.
- Once entered, trade remains open until TP or SL.
- M1 data resolves execution ordering.
- Bid-candle model; optional spread/slippage can be configured later.

## Outputs
Trades CSV plus overall and per-pair summaries: setups, filled/expired, wins/losses, win rate, average R:R, expectancy (R), profit factor, cumulative R, max drawdown (R), max drawdown % at configurable risk-per-trade, and max losing streak.

## Run
```
pip install -r requirements.txt
python -m src.backtest --data-dir data --out-dir results
```

Input CSVs should be one M1 file per pair named e.g. `EURUSD.csv` with columns:
`timestamp,open,high,low,close`. Timestamps must be UTC.

A GitHub Actions workflow is included for tests. Large historical datasets should not be committed to Git.
