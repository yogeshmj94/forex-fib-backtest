def streak(a):
 b=c=0
 for r in a:
  if r<0:c+=1;b=max(b,c)
  else:c=0
 return b
def summarize(d,risk=1.):
 x=d[d.status.isin(["win","loss","loss_ambiguous"])].copy();w=(x.result_r>0).sum();l=(x.result_r<0).sum();eq=x.result_r.cumsum();dd=eq-eq.cummax();gw=float(x.loc[x.result_r>0,"result_r"].sum());gl=float(-x.loc[x.result_r<0,"result_r"].sum());md=float(-dd.min()) if len(dd) else 0
 return {"setups":len(d),"ob_found":int(d.timeframe.notna().sum()),"no_ob":int((d.status=="no_ob").sum()),"filled":int(d.status.isin(["win","loss","loss_ambiguous","open"]).sum()),"expired":int((d.status=="expired").sum()),"wins":int(w),"losses":int(l),"win_rate_pct":100*w/(w+l) if w+l else 0,"avg_rr":float(x.loc[x.result_r>0,"rr"].mean()) if w else 0,"expectancy_r":float(x.result_r.mean()) if len(x) else 0,"profit_factor":gw/gl if gl else None,"cumulative_r":float(x.result_r.sum()),"max_drawdown_r":md,"max_drawdown_pct_fixed_risk":md*risk,"max_losing_streak":streak(x.result_r.tolist()),"trades_rr_gte_1_5":int((x.rr>=1.5).sum()),"timeframes":{str(k):int(v) for k,v in d.timeframe.dropna().value_counts().items()}}
