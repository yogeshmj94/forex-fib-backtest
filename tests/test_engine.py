import pandas as pd
from src.engine import orders_from_h4,simulate

def h4(rows):
    return pd.DataFrame(rows,columns=["timestamp","open","high","low","close"])

def test_bullish_order_and_fill_win():
    x=h4([
      [pd.Timestamp("2026-01-01T00:00Z"),1.08,1.087,1.08,1.086],
      [pd.Timestamp("2026-01-01T04:00Z"),1.086,1.092,1.085,1.09],
      [pd.Timestamp("2026-01-01T08:00Z"),1.09,1.091,1.084,1.085]])
    o=orders_from_h4("EURUSD",x)[0]
    m=pd.DataFrame([
      [pd.Timestamp("2026-01-01T08:01Z"),1.09,1.09,1.0847,1.085],
      [pd.Timestamp("2026-01-01T08:02Z"),1.085,1.093,1.085,1.092]
    ],columns=["timestamp","open","high","low","close"])
    r=simulate(o,m); assert r["status"]=="win"

def test_expired_if_not_filled_in_live():
    x=h4([
      [pd.Timestamp("2026-01-01T00:00Z"),1.08,1.087,1.08,1.086],
      [pd.Timestamp("2026-01-01T04:00Z"),1.086,1.092,1.085,1.09],
      [pd.Timestamp("2026-01-01T08:00Z"),1.09,1.091,1.087,1.088]])
    o=orders_from_h4("EURUSD",x)[0]
    m=pd.DataFrame([[pd.Timestamp("2026-01-01T08:01Z"),1.09,1.091,1.087,1.088]],columns=["timestamp","open","high","low","close"])
    assert simulate(o,m)["status"]=="expired"
