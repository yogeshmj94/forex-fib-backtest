# H4 Impulse & Momentum Research

## Scope and status

**GitHub Actions run:** 35203110034  
**Period:** 15 Sep 2025 through 15 Sep 2026  
**Universe:** 20 FX pairs  
**OB timeframes:** M15, M5, M3 only  
**Stop buffer:** 3 pips  
**Target:** Live-1 structural high/low  
**Filled trades:** 1,607  

This is **post-OOS research/model-development data**, not a new untouched OOS validation. Findings below are hypotheses to encode and validate on independent data before changing production rules.

## Machine-readable momentum definition

The visual premise is that Live-1 must demonstrate enough directional momentum beyond Live-2 structure to make a later revisit of the Live-1 extreme plausible.

For bullish setups:

- `impulse_pips = (Live1.high - Live2.low) / pip_size`
- `breakout_pips = (Live1.close - Live2.high) / pip_size`
- `momentum_pct = breakout_pips / impulse_pips * 100`

For bearish setups the calculation is direction-normalized:

- `impulse_pips = (Live2.high - Live1.low) / pip_size`
- `breakout_pips = (Live2.low - Live1.close) / pip_size`
- `momentum_pct = breakout_pips / impulse_pips * 100`

The diagnostic uses the actual preceding H4 row as Live-2 rather than assuming exactly four clock-hours earlier, so source-data gaps do not corrupt the relationship.

## Overall distribution

Across the 1,607 filled trades:

| Measure | Mean | Median |
|---|---:|---:|
| Directional impulse | 42.36 pips | 35.90 pips |
| Breakout beyond Live-2 structure | 9.54 pips | 6.70 pips |
| Momentum % | 22.64% | 20.21% |
| Trade expectancy | +0.1317R | — |
| Total result | +211.71R | — |

## Outcome by impulse size

| Impulse pips | Trades | Win rate | Expectancy | Total R | Avg winning RR |
|---|---:|---:|---:|---:|---:|
| <20 | 288 | 41.32% | +0.0659R | +18.99R | 1.580R |
| 20–30 | 337 | 41.25% | +0.2029R | +68.39R | 1.916R |
| 30–40 | 277 | 37.91% | +0.1429R | +39.59R | 2.015R |
| 40–50 | 222 | 37.39% | +0.2083R | +46.24R | 2.232R |
| 50–60 | 158 | 36.08% | +0.1730R | +27.33R | 2.251R |
| 60–80 | 190 | 32.63% | +0.1453R | +27.61R | 2.510R |
| 80–100 | 76 | 26.32% | -0.1220R | -9.27R | 2.336R |
| 100+ | 59 | 23.73% | -0.1215R | -7.17R | 2.702R |

### Impulse interpretation

Impulse is **not monotonically better when larger**. The useful region is broad from roughly 20 to 80 pips. Very large H4 impulses (80+ pips) were negative in this sample despite larger available reward. This is consistent with an exhaustion/overextension hypothesis: a pair can show a large move without that move being a good retracement-and-continuation setup.

A simple `<80 pip` filter would have retained 1,472 trades and increased expectancy from +0.1317R to +0.1550R, but this is an in-sample diagnostic and must not be adopted as a rule without independent validation.

## Outcome by normalized momentum

| Momentum % | Trades | Win rate | Expectancy | Total R | Avg winning RR |
|---|---:|---:|---:|---:|---:|
| 0–5% | 203 | 35.47% | +0.0989R | +20.08R | 2.098R |
| 5–10% | 213 | 37.56% | +0.1107R | +23.59R | 1.957R |
| 10–15% | 187 | 34.76% | +0.0491R | +9.19R | 2.018R |
| 15–20% | 193 | 31.09% | **-0.0570R** | **-11.00R** | 2.033R |
| 20–25% | 164 | 40.24% | +0.2144R | +35.16R | 2.018R |
| 25–30% | 155 | 42.58% | +0.2660R | +41.23R | 1.973R |
| 30–35% | 133 | 45.11% | **+0.3354R** | **+44.61R** | 1.960R |
| 35–40% | 109 | 36.70% | +0.1694R | +18.47R | 2.187R |
| 40–50% | 156 | 33.33% | +0.0040R | +0.62R | 2.012R |
| 50%+ | 94 | 40.43% | +0.3167R | +29.77R | 2.257R |

### Momentum interpretation

The clearest broad feature is the improvement once momentum reaches roughly 20%. The 20–35% region was particularly strong. However, performance is **not monotonic**: 15–20% was negative, 40–50% was approximately flat, and 50%+ was strong again. Therefore the current data does not justify a claim that “more momentum is always better.”

Threshold diagnostics:

| Minimum momentum | Trades retained | Win rate | Expectancy | Total R |
|---|---:|---:|---:|---:|
| ≥5% | 1,404 | 37.54% | +0.1365R | +191.63R |
| ≥10% | 1,191 | 37.53% | +0.1411R | +168.05R |
| ≥15% | 1,004 | 38.05% | +0.1582R | +158.86R |
| ≥20% | 811 | 39.70% | **+0.2094R** | +169.86R |
| ≥25% | 647 | 39.57% | +0.2082R | +134.70R |
| ≥30% | 492 | 38.62% | +0.1900R | +93.47R |
| ≥35% | 359 | 36.21% | +0.1361R | +48.86R |
| ≥40% | 250 | 36.00% | +0.1216R | +30.39R |
| ≥50% | 94 | 40.43% | +0.3167R | +29.77R |

A ≥20% threshold is a natural hypothesis because it improved expectancy materially without selecting an extremely narrow range. It is **not frozen**; it needs independent validation.

## Joint impulse × momentum behavior

Expectancy (R/trade) by broad two-dimensional bucket:

| Impulse | Momentum 0–10% | 10–20% | 20–30% | 30–40% | 40%+ |
|---|---:|---:|---:|---:|---:|
| <20 pips | -0.007 | -0.078 | +0.385 | +0.209 | -0.130 |
| 20–40 | -0.013 | +0.148 | +0.393 | +0.230 | +0.191 |
| 40–60 | +0.466 | +0.078 | -0.109 | +0.347 | +0.177 |
| 60–80 | +0.218 | -0.157 | +0.086 | +0.294 | +0.549 |
| 80+ | -0.172 | -0.482 | +0.396 | +0.187 | -0.263 |

Cell sample sizes range from 18 to 162, so the extreme cells are noisy. The important conclusion is that **impulse size and normalized breakout momentum interact**; neither should be treated as a one-dimensional “bigger is better” variable.

The broad `momentum >=20% AND impulse <80 pips` diagnostic retained 746 trades, generated +163.69R and +0.2194R/trade. This is a candidate hypothesis only.

## Pair-level results before momentum control

| Pair | Trades | Win rate | Expectancy | Total R | Median impulse | Median momentum |
|---|---:|---:|---:|---:|---:|---:|
| USDJPY | 70 | 27.14% | -0.1148R | -8.04R | 50.25 | 18.65% |
| EURJPY | 64 | 29.69% | -0.0686R | -4.39R | 51.35 | 16.97% |
| NZDUSD | 62 | 35.48% | -0.0104R | -0.65R | 22.05 | 18.53% |
| GBPAUD | 72 | 29.17% | -0.0011R | -0.08R | 59.10 | 16.65% |
| GBPUSD | 104 | 32.69% | +0.0141R | +1.46R | 34.30 | 21.67% |
| AUDCAD | 73 | 34.25% | +0.0620R | +4.53R | 29.60 | 15.89% |
| EURNZD | 69 | 31.88% | +0.0638R | +4.40R | 58.10 | 23.82% |
| AUDUSD | 77 | 37.66% | +0.0839R | +6.46R | 25.90 | 18.72% |
| GBPJPY | 73 | 34.25% | +0.1157R | +8.44R | 60.40 | 17.20% |
| GBPNZD | 67 | 32.84% | +0.1215R | +8.14R | 70.60 | 19.84% |
| USDCAD | 103 | 37.86% | +0.1389R | +14.31R | 25.80 | 24.92% |
| EURGBP | 110 | 44.55% | +0.1603R | +17.63R | 14.90 | 24.54% |
| CADJPY | 71 | 39.44% | +0.1783R | +12.66R | 37.30 | 21.78% |
| EURAUD | 62 | 35.48% | +0.1904R | +11.80R | 53.90 | 12.87% |
| EURUSD | 86 | 38.37% | +0.1921R | +16.52R | 29.95 | 20.56% |
| USDCHF | 98 | 42.86% | +0.2280R | +22.34R | 25.10 | 20.19% |
| EURCHF | 104 | 48.08% | +0.2365R | +24.60R | 16.10 | 22.56% |
| AUDJPY | 71 | 38.03% | +0.2499R | +17.74R | 50.50 | 18.43% |
| CHFJPY | 53 | 41.51% | +0.3107R | +16.47R | 52.70 | 26.64% |
| GBPCAD | 118 | 41.53% | +0.3166R | +37.36R | 42.60 | 22.71% |

## Does momentum explain pair underperformance?

To test the manual-trading observation that pairs should become more similar once momentum quality is controlled, each trade was assigned to its global momentum bucket and each pair's actual expectancy was compared with the expectancy expected from that pair's momentum-bucket mix.

The largest negative residuals were:

| Pair | Actual expectancy | Momentum-mix expected | Residual | Residual total R |
|---|---:|---:|---:|---:|
| USDJPY | -0.1148R | +0.1078R | **-0.2227R/trade** | -15.59R |
| EURJPY | -0.0686R | +0.1049R | **-0.1735R/trade** | -11.11R |
| NZDUSD | -0.0104R | +0.1207R | -0.1311R/trade | -8.13R |
| GBPUSD | +0.0141R | +0.1307R | -0.1166R/trade | -12.13R |
| GBPAUD | -0.0011R | +0.0979R | -0.0991R/trade | -7.13R |

This means momentum composition **does not fully explain pair dispersion in this one-year sample**. USDJPY and EURJPY are the clearest disproportionate underperformers after controlling only for normalized momentum. GBPUSD also underperformed its momentum mix, although it remained slightly profitable overall.

However, a simple `momentum >=20%` filter changes the picture materially:

- USDJPY: 32 trades, +0.0217R/trade, +0.69R.
- EURJPY: 24 trades, +0.1862R/trade, +4.47R.
- GBPUSD: 59 trades, approximately +0.19R/trade when combined with the broad `<80 pip` impulse condition; its weakness is not universal.
- EURNZD becomes the conspicuous weak pair under `momentum >=20%`: 38 trades, -0.2230R/trade, -8.48R.
- GBPNZD is also weak under that threshold: 32 trades, -0.0680R/trade, -2.18R.

Therefore the current evidence **partially supports** the manual observation: momentum filtering rehabilitates some apparent laggards (especially the JPY examples), but it does not make every pair statistically interchangeable. Different pairs can still underperform within the same momentum regime, and the samples per pair become small after filtering.

No pair should be removed on this evidence. Pair removal would be retrospective selection on model-development data.

## Direction and OB-timeframe sanity checks

Direction was balanced:

- Bearish: 745 trades, +0.1208R/trade, +89.99R.
- Bullish: 862 trades, +0.1412R/trade, +121.72R.

OB timeframe:

- M15: 746 trades, +0.1386R/trade, +103.39R.
- M5: 620 trades, +0.0847R/trade, +52.52R.
- M3: 241 trades, +0.2315R/trade, +55.80R.

All three retained OB timeframes were positive. M3 was strongest in this sample; this is descriptive, not a reason to optimize timeframe selection again.

## Drawdown diagnostics

A chronological recalculation on this diagnostic CSV produced approximately 32.03R max drawdown for all 1,607 trades. This differs slightly from the earlier grid's reported 30.91R, so this diagnostic DD should be treated as an analysis estimate until the metrics implementation/order convention is reconciled.

Using the same chronological calculation consistently for comparisons:

- All trades: ~32.03R DD, +0.1317R/trade.
- Momentum >=20%: ~26.36R DD, +0.2094R/trade.
- Momentum 20–35% only: ~15.29R DD, +0.2677R/trade.
- Momentum >=20% and impulse <80 pips: ~22.36R DD, +0.2194R/trade.

The narrow 20–35% band looks attractive historically, but selecting both lower and upper momentum bounds from this same sample would carry substantial overfitting risk. Prefer testing a simple, visually motivated lower threshold (for example 20%) on independent data before considering a band-pass rule.

## Research conclusions

1. The visual concept of momentum can be encoded cleanly as the percentage of the Live-2-low/Live-1-high directional impulse that Live-1 closes beyond Live-2 structure (mirrored for bearish setups).
2. Raw H4 impulse magnitude is not “more is better.” 20–80 pips was broadly productive; 80+ pips was negative in this sample and may represent overextension/exhaustion.
3. Normalized momentum contains useful information. The broad >=20% region materially improved expectancy in this sample, with 20–35% especially strong.
4. The relationship is not monotonic, so no narrow optimum should be treated as a law. The 15–20% bucket was negative and 40–50% nearly flat, while 50%+ was strong again.
5. Momentum explains some apparent pair weakness but not all of it. USDJPY/EURJPY improved substantially after >=20% filtering, while EURNZD/GBPNZD became weak within that filtered subset.
6. There is no evidence here to justify permanently dropping GBPUSD or any other pair. The correct next test is whether a simple momentum rule improves pair consistency on independent data.
7. No production rule has been changed by this analysis.

## Follow-up D1 structural-target research

These later experiments used the same 15 Sep 2025–15 Sep 2026 research period
and the experimental M15/M5/M3 OB set. They are documented here so rejected
ideas and useful interactions are not lost. None of the D1 variables below is
part of the production strategy.

### Completed D1 extreme as target and H4-room filter

**Run:** GitHub Actions run 35208313846

For bullish setups, the completed Live-1 D1 high replaced the Live-1 H4 high as
the structural target; bearish setups mirrored this with the D1 low. A setup
was invalid if the D1 target was at or behind the Live-1 H4 extreme, including
equality. The equality rule represented the assumption that spread may already
have consumed an apparently equal liquidity level.

| Diagnostic | Result |
|---|---:|
| Initial setups | 10,974 |
| Invalidated by D1/H4 structure | 6,358 |
| D1-valid setups | 4,616 |
| Setups with OB | 2,940 |
| Filled trades | 787 |
| Wins / losses | 172 / 614 |
| Win rate | 21.88% |
| Average winning RR | 3.83R |
| Cumulative result | +45.08R |
| Profit factor | 1.073 |
| Max drawdown | 33.30R |
| Max losing streak | 19 |

The D1 rule removed about 58% of initial setups but left only marginal positive
expectancy and a 9.99% drawdown at the configured 0.30% risk. It therefore did
not justify replacing the production fixed-1R target.

### Live-2 H4 proximity to completed D1 support/resistance

**Run:** GitHub Actions run 35210518016

The signed distance separated an actual D1 sweep (`<0`) from exact touch (`=0`)
and candles merely near the level. Bullish trades measured Live-2 H4 low minus
the completed D1 low; bearish trades used the mirrored high calculation.

| Live-2 interaction | Trades | Win rate | Avg R | Total R |
|---|---:|---:|---:|---:|
| Swept | 232 | 18.1% | -0.073R | -16.86R |
| Exact touch | 11 | 36.4% | +1.104R | +12.15R |
| 0–5 pips away | 89 | 24.7% | +0.246R | +21.89R |
| 5–10 pips away | 97 | 23.7% | +0.173R | +16.74R |
| 10–20 pips away | 130 | 17.7% | -0.128R | -16.62R |
| More than 20 pips away | 227 | 25.6% | +0.122R | +27.78R |

Sweep plus reclaim was not beneficial: 120 such trades won 16.7% and returned
-23.66R. The 112 sweeps without reclaim returned +6.81R. Proximity was also
non-monotonic, so neither a sweep requirement nor a simple maximum-distance
filter was adopted.

### D1 proximity × impulse × momentum × structural room

**Run:** GitHub Actions run 35211367520

The full five-dimensional table was too sparse: no complete combination cell
had at least ten trades. It must not be used to select a narrow positive setup.
The simpler two-variable tables did expose useful hypotheses:

| Impulse | Momentum | Trades | Win rate | Avg R | Total R |
|---|---:|---:|---:|---:|---:|
| 15–25 pips | 20–30% | 35 | 40.0% | +0.84R | +29.44R |
| <=15 pips | <=10% | 25 | 36.0% | +0.66R | +16.42R |
| <=15 pips | 30–40% | 17 | 41.2% | +0.48R | +8.09R |
| 25–35 pips | 30–40% | 23 | 30.4% | +0.33R | +7.52R |
| 35–50 pips | 30–40% | 24 | 29.2% | +0.31R | +7.47R |

Momentum of 10–20% was consistently weak with larger impulses: the 25–35,
35–50 and >50-pip impulse groups returned approximately -14.2R, -13.1R and
-22.6R. When impulse/remaining-room was 1–2x, momentum <=10% returned -23.74R
and momentum 10–20% returned -26.53R across 98 combined trades. Conversely,
when impulse/room exceeded 2x, strong momentum remained productive: >40%
momentum returned +25.48R across 48 trades and 30–40% returned +18.89R across
48 trades.

D1 interaction depended on momentum as well. The 0–5-pip/30–40% group returned
+16.09R across 16 trades; 5–10 pips/30–40% returned +18.75R across 19 trades.
An actual D1 sweep with only 10–20% momentum returned -28.38R across 52 trades.

**Interpretation:** momentum appears to distinguish continuation from
exhaustion after accounting for impulse and available room. The positive cells
are too small to become production entry rules. The broader negative 10–20%
momentum interaction is a candidate exclusion hypothesis for an independent
test, not a current filter.

## Production decision after the research sequence

- Restore the frozen H4/session/entry framework, 3-pip buffer and fixed 1R TP.
- Do not use D1 targets, D1/H4 invalidation, D1 proximity, sweep/reclaim,
  impulse, momentum or structural-room filters in production.
- Use M15, M5 and M2 for production OB detection, in that priority order.
- Exclude M3 and M1 from OB detection. Continue using M1 price data to resolve
  fills and same-candle TP/SL ordering.
- Retain all 20 currency pairs and all other production parameters.

## Next validation test

Freeze the **hypothesis**, not the threshold outcome: `Live-1 breakout strength relative to the complete two-candle impulse should be materially large enough to demonstrate continuation momentum.`

The clean next experiment is an independent-period validation comparing the existing setup against a small number of pre-declared momentum rules, preferably `no filter` versus `momentum >=20%`, while retaining the existing pair universe. Report portfolio expectancy/DD plus pair-level residual dispersion. Do not search additional thresholds on that validation period.
