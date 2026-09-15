from dataclasses import dataclass
import pandas as pd
TFS=[("M15","15min"),("M5","5min"),("M3","3min"),("M2","2min"),("M1","1min")]
def pip_size(s): return .01 if s.endswith("JPY") else .0001
def resample(d,r): return d.set_index("timestamp").resample(r,origin="start_day",label="left",closed="left").agg({"open":"first","high":"max","low":"min","close":"last"}).dropna().reset_index()
def to_h4(m): return resample(m,"4h")
@dataclass
class Setup:
 symbol:str;direction:str;signal_time:object;live_start:object;live_end:object;fib60:float;fib80:float;stop:float;target:float
def setups_from_h4(s,h,bufp=5):
 out=[];buf=bufp*pip_size(s)
 for i in range(2,len(h)):
  a,b=h.iloc[i-2],h.iloc[i-1];st=h.iloc[i].timestamp;en=st+pd.Timedelta(hours=4)
  if b.close>a.high:
   hi,lo=b.high,a.low;out.append(Setup(s,"bullish",b.timestamp,st,en,hi-.6*(hi-lo),hi-.8*(hi-lo),lo-buf,hi))
  elif b.close<a.low:
   hi,lo=a.high,b.low;out.append(Setup(s,"bearish",b.timestamp,st,en,lo+.6*(hi-lo),lo+.8*(hi-lo),hi+buf,lo))
 return out
def find_ob(x,m):
 # OB must exist before Live begins and may form in Live-2 or Live-1.
 pre_start=x.signal_time-pd.Timedelta(hours=4)
 pre=m[(m.timestamp>=pre_start)&(m.timestamp<x.live_start)]
 zlo,zhi=sorted((x.fib60,x.fib80))
 for name,rule in TFS:
  t=resample(pre,rule)
  for j in range(1,len(t)):
   crossed=t.iloc[j].high>=x.fib60 if x.direction=="bullish" else t.iloc[j].low<=x.fib60
   if not crossed: continue
   for k in range(j-1,-1,-1):
    o=t.iloc[k];opp=o.close<o.open if x.direction=="bullish" else o.close>o.open
    if not opp: continue
    entry=o.low if x.direction=="bullish" else o.high
    if zlo<=entry<=zhi:return name,o.timestamp,entry
   break
 return None
def simulate(x,m,tp_mode="fixed2r"):
 ob=find_ob(x,m)
 if not ob:return {"status":"no_ob","timeframe":None,"ob_time":None,"entry":None,"rr":None,"fill_time":None,"exit_time":None,"result_r":0.}
 tf,ot,e=ob;risk=e-x.stop if x.direction=="bullish" else x.stop-e
 # Fixed 2R target: preserve entry and stop, set TP exactly two risks away.
 target=e+2*risk if x.direction=="bullish" else e-2*risk
 rew=2*risk
 if risk<=0 or rew<=0:return {"status":"invalid_ob","timeframe":tf,"ob_time":ot,"entry":e,"rr":None,"fill_time":None,"exit_time":None,"result_r":0.}
 rr=rew/risk;fill=None
 # Pending order becomes active only after Live-1 has closed.
 for _,b in m[(m.timestamp>=x.live_start)&(m.timestamp<x.live_end)].iterrows():
  if b.low<=e<=b.high:fill=b.timestamp;break
 if fill is None:return {"status":"expired","timeframe":tf,"ob_time":ot,"entry":e,"rr":rr,"fill_time":None,"exit_time":None,"result_r":0.}
 for _,b in m[m.timestamp>=fill].iterrows():
  sl=b.low<=x.stop if x.direction=="bullish" else b.high>=x.stop;tp=b.high>=target if x.direction=="bullish" else b.low<=target
  if sl and tp:return {"status":"loss_ambiguous","timeframe":tf,"ob_time":ot,"entry":e,"target":target,"rr":rr,"fill_time":fill,"exit_time":b.timestamp,"result_r":-1.}
  if sl:return {"status":"loss","timeframe":tf,"ob_time":ot,"entry":e,"rr":rr,"fill_time":fill,"exit_time":b.timestamp,"result_r":-1.}
  if tp:return {"status":"win","timeframe":tf,"ob_time":ot,"entry":e,"target":target,"rr":rr,"fill_time":fill,"exit_time":b.timestamp,"result_r":rr}
 return {"status":"open","timeframe":tf,"ob_time":ot,"entry":e,"rr":rr,"fill_time":fill,"exit_time":None,"result_r":0.}
