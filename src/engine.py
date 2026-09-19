from dataclasses import dataclass
import pandas as pd

# Production OB priority. M1 and M2 are excluded.
TFS=[("M15","15min"),("M5","5min"),("M3","3min")]

def pip_size(s): return .01 if s.endswith("JPY") else .0001

def resample(d,r):
 return d.set_index("timestamp").resample(r,origin="start_day",label="left",closed="left").agg({"open":"first","high":"max","low":"min","close":"last"}).dropna().reset_index()

def to_h4(m): return resample(m,"4h")

@dataclass
class Setup:
 symbol:str;direction:str;signal_time:object;live_start:object;live_end:object
 fib60:float;fib80:float;stop:float;target:float
 expansion_start:object;expansion_low:float;expansion_high:float;expansion_candles:int

def _expansion_segment(h,i,direction):
 # Walk backwards from Live-1 to the most recent confirmed opposing H4
 # retracement. User rule: bullish retracement is confirmed by a close below
 # the preceding candle's low; bearish is the mirror. The fib anchors are the
 # actual lowest/highest prices in the resulting expansion leg, not a fixed
 # Live-2/Live-1 pair.
 start=0
 if direction=="bullish":
  for j in range(i-1,0,-1):
   if h.iloc[j].close < h.iloc[j-1].low:
    start=j
    break
 else:
  for j in range(i-1,0,-1):
   if h.iloc[j].close > h.iloc[j-1].high:
    start=j
    break
 seg=h.iloc[start:i+1]
 return start,seg

def setups_from_h4(s,h,bufp=5):
 out=[];buf=bufp*pip_size(s)
 for i in range(2,len(h)):
  a,b=h.iloc[i-2],h.iloc[i-1];st=h.iloc[i].timestamp;en=st+pd.Timedelta(hours=4)
  if b.close>a.high:
   start,seg=_expansion_segment(h,i-1,"bullish")
   lo=float(seg.low.min());hi=float(b.high)
   # Live-1 must be the high of the measured expansion; otherwise the leg
   # already peaked before Live-1 and this is not a fresh expansion endpoint.
   if float(seg.high.max())>hi: continue
   out.append(Setup(s,"bullish",b.timestamp,st,en,hi-.6*(hi-lo),hi-.8*(hi-lo),lo-buf,hi,h.iloc[start].timestamp,lo,hi,len(seg)))
  elif b.close<a.low:
   start,seg=_expansion_segment(h,i-1,"bearish")
   hi=float(seg.high.max());lo=float(b.low)
   if float(seg.low.min())<lo: continue
   out.append(Setup(s,"bearish",b.timestamp,st,en,lo+.6*(hi-lo),lo+.8*(hi-lo),hi+buf,lo,h.iloc[start].timestamp,lo,hi,len(seg)))
 return out

def find_ob(x,m):
 # Search the complete measured expansion for the OB. It must exist before
 # Live begins; the pending order itself can fill only during Live.
 pre=m[(m.timestamp>=x.expansion_start)&(m.timestamp<x.live_start)]
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

def simulate(x,m,tp_mode="fixed2r",rr_value=2.0):
 ob=find_ob(x,m)
 if not ob:return {"status":"no_ob","timeframe":None,"ob_time":None,"entry":None,"rr":None,"fill_time":None,"exit_time":None,"result_r":0.}
 tf,ot,e=ob;risk=e-x.stop if x.direction=="bullish" else x.stop-e
 if tp_mode=="live1":
  target=x.target
  rew=target-e if x.direction=="bullish" else e-target
 elif tp_mode=="fixed":
  target=e+rr_value*risk if x.direction=="bullish" else e-rr_value*risk
  rew=rr_value*risk
 else:
  raise ValueError(f"Unknown tp_mode: {tp_mode}")
 if risk<=0 or rew<=0:return {"status":"invalid_ob","timeframe":tf,"ob_time":ot,"entry":e,"rr":None,"fill_time":None,"exit_time":None,"result_r":0.}
 rr=rew/risk;fill=None
 for _,b in m[(m.timestamp>=x.live_start)&(m.timestamp<x.live_end)].iterrows():
  if b.low<=e<=b.high:fill=b.timestamp;break
 if fill is None:return {"status":"expired","timeframe":tf,"ob_time":ot,"entry":e,"target":target,"rr":rr,"fill_time":None,"exit_time":None,"result_r":0.}
 for _,b in m[m.timestamp>=fill].iterrows():
  sl=b.low<=x.stop if x.direction=="bullish" else b.high>=x.stop
  tp=b.high>=target if x.direction=="bullish" else b.low<=target
  if sl and tp:return {"status":"loss_ambiguous","timeframe":tf,"ob_time":ot,"entry":e,"target":target,"rr":rr,"fill_time":fill,"exit_time":b.timestamp,"result_r":-1.}
  if sl:return {"status":"loss","timeframe":tf,"ob_time":ot,"entry":e,"target":target,"rr":rr,"fill_time":fill,"exit_time":b.timestamp,"result_r":-1.}
  if tp:return {"status":"win","timeframe":tf,"ob_time":ot,"entry":e,"target":target,"rr":rr,"fill_time":fill,"exit_time":b.timestamp,"result_r":rr}
 return {"status":"open","timeframe":tf,"ob_time":ot,"entry":e,"target":target,"rr":rr,"fill_time":fill,"exit_time":None,"result_r":0.}
