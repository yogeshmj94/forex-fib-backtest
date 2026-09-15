import pandas as pd

def max_losing_streak(results):
    best=cur=0
    for r in results:
        if r<0: cur+=1; best=max(best,cur)
        else: cur=0
    return best

def summarize(df,risk_pct=1.0):
    setups=len(df); filled=df.status.ne("expired").sum()
    closed=df.status.isin(["win","loss","loss_ambiguous"])
    x=df[closed].copy(); wins=(x.result_r>0).sum(); losses=(x.result_r<0).sum()
    equity=x.result_r.cumsum(); peak=equity.cummax(); dd=equity-peak
    max_dd_r=float(-dd.min()) if len(dd) else 0.0
    gross_win=float(x.loc[x.result_r>0,"result_r"].sum())
    gross_loss=float(-x.loc[x.result_r<0,"result_r"].sum())
    return {
      "setups":int(setups),"filled":int(filled),"expired":int((df.status=="expired").sum()),
      "wins":int(wins),"losses":int(losses),
      "win_rate_pct":float(100*wins/(wins+losses)) if wins+losses else 0,
      "avg_rr":float(x.loc[x.result_r>0,"rr"].mean()) if wins else 0,
      "expectancy_r":float(x.result_r.mean()) if len(x) else 0,
      "profit_factor":gross_win/gross_loss if gross_loss else None,
      "cumulative_r":float(x.result_r.sum()),"max_drawdown_r":max_dd_r,
      "max_drawdown_pct_fixed_risk":max_dd_r*risk_pct,
      "max_losing_streak":max_losing_streak(x.result_r.tolist()),
      "trades_rr_gte_1_5":int((df.loc[df.status.ne("expired"),"rr"]>=1.5).sum())
    }
