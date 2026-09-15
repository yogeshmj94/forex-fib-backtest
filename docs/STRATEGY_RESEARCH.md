# Strategy Research & Validation Log

## Purpose

This document records the strategy optimisation and validation process so that parameter discovery, implementation mistakes, frozen rules, and genuinely out-of-sample evidence remain distinguishable.

The strategy is evaluated as a portfolio across 20 liquid FX pairs. Results are expressed primarily in R so risk sizing can be evaluated separately from the trading edge.

## Research rules

- Optimisation-period results may be used to select parameters.
- Once a parameter is frozen, later out-of-sample (OOS) data is not used to retune it.
- Invalid runs caused by implementation/workflow bugs are retained in the history but excluded from trading conclusions.
- Risk percentages below are fixed percentages of initial account size; no compounding is assumed.
- The current frozen trading configuration is **3-pip stop buffer + fixed 1R TP**.
- Current risk model is **0.30% of initial account size per trade, fixed, no compounding**.

## Frozen configuration

| Parameter | Frozen value |
|---|---|
| Universe | 20 FX pairs |
| Stop buffer | 3 pips |
| Take profit | Fixed 1R |
| Risk per trade | 0.30% of initial account size |
| Compounding | None |
| Entry / OB / session rules | Unchanged from optimisation implementation |

**Freeze boundary:** parameter discovery ended before the Sep 2023–Sep 2025 OOS test. The OOS period must not be used to retune the frozen parameters.

---

## Experiment 1 — Stop-buffer sweep

**Run:** GitHub Actions run 34958041369  
**Purpose:** Determine whether adding a stop buffer improves the strategy and whether performance is stable across nearby values.  
**TP during this experiment:** fixed 2R.

| Buffer | Win rate | Expectancy (R/trade) | Profit factor | Total R | Max DD (R) | Max losing streak |
|---:|---:|---:|---:|---:|---:|---:|
| 0 pip | 36.84% | 0.1051 | 1.166 | 192 | 32 | 12 |
| 2 pip | 36.31% | 0.0893 | 1.140 | 163 | 25 | 12 |
| **3 pip** | **36.60%** | **0.0981** | **1.155** | **179** | **24** | **15** |
| 5 pip | 36.99% | 0.1096 | 1.174 | 200 | 31 | 15 |
| 7 pip | 37.15% | 0.1145 | 1.182 | 209 | 35 | 15 |
| 10 pip | 36.99% | 0.1096 | 1.174 | 200 | 31 | 15 |

**Interpretation:** all tested buffers remained profitable. There was no isolated “magic” buffer. Three pips retained positive expectancy while producing the lowest max drawdown of the main candidates.

**Decision:** freeze the stop buffer at **3 pips** for TP optimisation.

---

## Invalid TP experiment — excluded

**Run:** GitHub Actions run 34965143590

The first TP sweep returned the same 2R statistics for Live-1, 1.5R, 2R, 2.5R and 3R. Investigation found that the simulation function accepted TP parameters but still hard-coded:

`target = entry ± 2 * risk` and `reward = 2 * risk`.

Therefore this run is **INVALID and excluded from all strategy conclusions**.

The engine was corrected and the workflow was given sanity checks that verify requested fixed-R values are actually reflected in `avg_rr`.

---

## Experiment 2 — Broad TP sweep

**Run:** GitHub Actions run 34971910096  
**Stop buffer:** fixed at 3 pips.

| TP | Win rate | Avg winning RR | Expectancy | Profit factor | Total R | Max DD (R) | Max losing streak |
|---|---:|---:|---:|---:|---:|---:|---:|
| Live-1 structural | 37.10% | 2.012 | **0.1174** | 1.187 | **214.28** | 29.04 | 12 |
| 1.5R | 44.14% | 1.50 | 0.1035 | 1.185 | 189 | **18.5** | **11** |
| 2R | 36.60% | 2.00 | 0.0981 | 1.155 | 179 | 24 | 15 |
| 2.5R | 31.34% | 2.50 | 0.0970 | 1.141 | 177 | 26.5 | 15 |
| 3R | 27.30% | 3.00 | 0.0921 | 1.127 | 168 | 41 | 16 |

**Interpretation:** increasingly ambitious fixed targets reduced win rate without improving expectancy. Live-1 produced the highest raw expectancy/total R, while 1.5R substantially reduced drawdown.

**Decision:** run a narrower fixed-TP test around/below 1.5R.

---

## Experiment 3 — Narrow TP sweep

**Run:** GitHub Actions run 34977969713  
**Stop buffer:** fixed at 3 pips.

| TP | Win rate | Expectancy | Profit factor | Total R | Max DD (R) | Max losing streak |
|---|---:|---:|---:|---:|---:|---:|
| **1R** | **55.42%** | **0.1084** | **1.243** | **198** | **18** | **7** |
| 1.25R | 49.23% | 0.1077 | 1.212 | 196.75 | 19.75 | 11 |
| 1.5R | 44.14% | 0.1035 | 1.185 | 189 | 18.5 | 11 |
| 1.75R | 39.70% | 0.0919 | 1.152 | 167.75 | 23.25 | 11 |
| Live-1 | 37.10% | 0.1174 | 1.187 | 214.28 | 29.04 | 12 |

**Interpretation:** 1R–1.5R formed a broad positive-expectancy region rather than a narrow optimum. Fixed 1R produced the strongest combination of win rate, profit factor, total R and drawdown for a drawdown-constrained prop-account objective.

**Decision:** freeze TP at **1R**. Do not continue micro-optimising TP on the same sample.

---

## Risk decision

Risk was set to **0.30% of initial account size per trade with no compounding** before the 24-month OOS validation.

This is a risk-sizing decision rather than a change to the underlying trade signal.

---

## Experiment 4 — 24-month out-of-sample validation

**Run:** GitHub Actions run 34987939985  
**Period:** 15 Sep 2023 through 15 Sep 2025  
**Status:** VALID OOS — parameters were frozen before this dataset was evaluated.

Preflight confirmed:

- 20 pairs
- 3-pip stop buffer
- fixed 1R TP
- 0.30% fixed risk
- no parameter optimisation against this period

### Portfolio result

| Metric | OOS result |
|---|---:|
| H4 setups | 21,425 |
| OB found | 17,156 |
| No OB | 4,269 |
| Filled trades | 3,610 |
| Wins | 1,950 |
| Losses | 1,660 |
| Win rate | **54.02%** |
| Average RR | **1.00R** |
| Expectancy | **+0.0803R/trade** |
| Profit factor | **1.175** |
| Cumulative result | **+290R** |
| Max drawdown | **22R** |
| Max DD at 0.30% fixed risk | **6.6%** |
| Max losing streak | **10** |

### Comparison with optimisation-period 1R result

| Metric | Optimisation period | 24-month OOS |
|---|---:|---:|
| Win rate | 55.42% | 54.02% |
| Expectancy | +0.1084R | +0.0803R |
| Profit factor | 1.243 | 1.175 |
| Max DD | 18R | 22R |
| Max losing streak | 7 | 10 |

**Interpretation:** performance weakened modestly out of sample, as expected, but remained clearly positive across 3,610 OOS trades. The similarity of win rate and continued positive expectancy is materially stronger evidence than the optimisation-period result alone.

**Decision:** accept the OOS result without retuning the strategy.

---

## Known implementation/research issues

Several workflow/code errors occurred while building the experiment harness. They are not trading losses and must not be interpreted as strategy results:

1. Literal `\\n` characters in a GitHub Actions shell loop caused Bash syntax errors.
2. A literal `\\n` in `src/backtest.py` caused a Python syntax error.
3. Nested result directories initially used `mkdir(exist_ok=True)` without `parents=True`.
4. The first TP sweep accepted TP arguments but the engine still hard-coded 2R; that entire run is explicitly invalid.
5. Historical GitHub Actions runs may display the current workflow name even though they ran older workflow definitions. Use run IDs/commit SHAs and dataset dates rather than the UI title as experimental evidence.

---

## Next research stages

1. **Pair-by-pair robustness analysis** — determine whether portfolio expectancy is broadly distributed across the 20 pairs or concentrated in a few symbols.
2. **Monte Carlo / risk-of-ruin analysis** — use the frozen trade outcomes to estimate the distribution of max drawdown at fixed risk sizes, especially 0.30%, and probabilities of breaching prop-firm limits.
3. **Risk sizing decision** — decide whether 0.30% provides enough safety margin or whether production risk should be lower.
4. **Forward test** — implement the frozen strategy in the EA and compare its executions with the Python reference implementation.
5. **Live/demo evidence** — accumulate a forward track record without changing the frozen strategy in response to short-term performance.

The Nifty 50 cross-market test has intentionally been dropped from the current research plan.

## Research principle

The objective is not to find the historical parameter combination with the highest return. The objective is to identify a stable, explainable edge that remains positive under nearby parameter choices, unseen historical data, realistic risk constraints, and eventually forward execution.
