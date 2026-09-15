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

## OOS pair-by-pair robustness

The 24-month OOS artifact from run 34987939985 was inspected at symbol level.

| Pair | Trades | Win rate | Expectancy R | PF | Total R | Max DD R |
|---|---:|---:|---:|---:|---:|---:|
| AUDCAD | 133 | 59.40% | +0.1880 | 1.463 | +25 | 10 |
| AUDJPY | 119 | 42.86% | -0.1429 | 0.750 | -17 | 19 |
| AUDUSD | 168 | 52.98% | +0.0595 | 1.127 | +10 | 10 |
| CADJPY | 191 | 56.54% | +0.1309 | 1.301 | +25 | 12 |
| CHFJPY | 171 | 58.48% | +0.1696 | 1.408 | +29 | 9 |
| EURAUD | 145 | 54.48% | +0.0897 | 1.197 | +13 | 7 |
| EURCHF | 214 | 54.67% | +0.0935 | 1.206 | +20 | 12 |
| EURGBP | 258 | 53.10% | +0.0620 | 1.132 | +16 | 11 |
| EURJPY | 180 | 47.78% | -0.0444 | 0.915 | -8 | 21 |
| EURNZD | 113 | 54.87% | +0.0973 | 1.216 | +11 | 5 |
| EURUSD | 260 | 51.54% | +0.0308 | 1.063 | +8 | 17 |
| GBPAUD | 119 | 60.50% | +0.2101 | 1.532 | +25 | 6 |
| GBPCAD | 193 | 52.85% | +0.0570 | 1.121 | +11 | 14 |
| GBPJPY | 188 | 48.40% | -0.0319 | 0.938 | -6 | 20 |
| GBPNZD | 119 | 68.91% | +0.3782 | 2.216 | +45 | 8 |
| GBPUSD | 246 | 55.69% | +0.1138 | 1.257 | +28 | 10 |
| NZDUSD | 149 | 51.01% | +0.0201 | 1.041 | +3 | 17 |
| USDCAD | 266 | 54.51% | +0.0902 | 1.198 | +24 | 15 |
| USDCHF | 221 | 53.85% | +0.0769 | 1.167 | +17 | 9 |
| USDJPY | 157 | 53.50% | +0.0701 | 1.151 | +11 | 15 |

**Breadth:** 17 of 20 pairs were profitable OOS; only AUDJPY (-17R), EURJPY (-8R), and GBPJPY (-6R) were negative. The profitable portfolio result is therefore not dependent on only one or two symbols.

**Concentration:** the strongest pair, GBPNZD, contributed 45R of the 290R portfolio total (15.5%). The top five contributors (GBPNZD, CHFJPY, GBPUSD, AUDCAD and CADJPY) contributed 152R (52.4%). Performance is concentrated to some degree, but not dominated by a single pair.

**JPY observation:** three losing pairs were JPY crosses (AUDJPY, EURJPY, GBPJPY), but CHFJPY, CADJPY and USDJPY were profitable. This is worth monitoring in forward data, but it is not a basis for removing JPY pairs after observing the OOS results.

**Decision:** retain all 20 pairs in the frozen strategy. Removing the three OOS losers now would be retrospective optimisation and would contaminate the validation discipline.

---

## Portfolio clustering and daily-risk analysis

The 3,610 OOS filled trades were analyzed using their actual fill and exit timestamps, including the 111 conservative `loss_ambiguous` outcomes already counted as -1R by the backtester.

- **Maximum simultaneous open positions:** 8.
- At **0.20% fixed risk**, eight simultaneous full-risk positions represent **1.6% nominal open risk**.
- At 0.30%, the same cluster represents 2.4% nominal open risk.
- Concurrency at new entries was typically low: median 2 positions, 90th percentile 3, 95th percentile 4, and roughly 99th percentile 5 positions.
- **Worst historical realized exit-day:** 25 Apr 2024, **-9R** across 11 exits.
- At 0.20% fixed risk, -9R corresponds to **-1.8%** of initial account size; at 0.30%, -2.7%.
- There were 72 realized days at or below -3R, 22 at or below -5R, and 3 at or below -8R.
- Largest observed net currency concentration was six USD risk-units; JPY and AUD each reached five. This confirms that pair-level diversification does not eliminate common-currency clustering.

**Interpretation:** 0.20% fixed risk provides materially more room for clustered FX exposure than 0.30%. Historical daily losses were comfortably below common prop-firm total-loss limits, but daily-loss rules differ by firm and may be equity-based rather than closed-P&L based. Eight simultaneous positions can also experience correlated adverse movement, so nominal per-trade risk must not be interpreted as independent portfolio risk.

**Current production-risk candidate:** retain **0.20% fixed initial-account risk per trade, no compounding**, subject to the exact daily/equity drawdown rules of whichever prop firms are selected.

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
