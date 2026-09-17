import pandas as pd
from src.metrics import summarize

def test_drawdown():
    df=pd.DataFrame({"status":["win","loss","loss","win"],"result_r":[1.5,-1,-1,1.5],"rr":[1.5,1.5,1.5,1.5],"timeframe":["M15"]*4})
    s=summarize(df,1.0)
    assert s["max_drawdown_r"]==2.0
    assert s["max_drawdown_pct_fixed_risk"]==2.0
    assert s["max_losing_streak"]==2
