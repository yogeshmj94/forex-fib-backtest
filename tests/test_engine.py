import pandas as pd

from src.engine import TFS, setups_from_h4, simulate


def frame(rows):
    return pd.DataFrame(
        rows, columns=["timestamp", "open", "high", "low", "close"]
    )


def bullish_setup():
    bars = frame([
        [pd.Timestamp("2026-01-01T00:00Z"), 1.080, 1.087, 1.080, 1.086],
        [pd.Timestamp("2026-01-01T04:00Z"), 1.086, 1.092, 1.085, 1.090],
        [pd.Timestamp("2026-01-01T08:00Z"), 1.090, 1.091, 1.084, 1.085],
    ])
    return setups_from_h4("EURUSD", bars, bufp=3)[0]


def pre_live_ob_rows():
    # A bearish M15 OB whose low is inside the 60%-80% retracement zone,
    # followed by a candle that crosses the 60% level.
    return [
        [pd.Timestamp("2026-01-01T03:45Z"), 1.0860, 1.0862, 1.0845, 1.0850],
        [pd.Timestamp("2026-01-01T04:00Z"), 1.0850, 1.0852, 1.0849, 1.0851],
    ]


def test_production_ob_timeframes():
    assert TFS == [("M15", "15min"), ("M5", "5min"), ("M2", "2min")]


def test_bullish_order_and_fill_win():
    x = bullish_setup()
    market = frame(pre_live_ob_rows() + [
        [pd.Timestamp("2026-01-01T08:01Z"), 1.0850, 1.0850, 1.0844, 1.0848],
        [pd.Timestamp("2026-01-01T08:02Z"), 1.0848, 1.0900, 1.0848, 1.0895],
    ])
    result = simulate(x, market, tp_mode="fixed", rr_value=1.0)
    assert result["status"] == "win"
    assert result["timeframe"] == "M15"


def test_expired_if_not_filled_in_live():
    x = bullish_setup()
    market = frame(pre_live_ob_rows() + [
        [pd.Timestamp("2026-01-01T08:01Z"), 1.0860, 1.0870, 1.0855, 1.0865],
    ])
    result = simulate(x, market, tp_mode="fixed", rr_value=1.0)
    assert result["status"] == "expired"
