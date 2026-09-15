from dataclasses import dataclass
import pandas as pd

def pip_size(symbol): return 0.01 if symbol.endswith("JPY") else 0.0001

def to_h4(m1):
    x=m1.set_index("timestamp")
    return x.resample("4h",origin="start_day",label="left",closed="left").agg({"open":"first","high":"max","low":"min","close":"last"}).dropna().reset_index()

@dataclass
class Order:
    symbol:str; direction:str; signal_time:object; live_start:object; live_end:object
    entry:float; stop:float; target:float; rr:float

def orders_from_h4(symbol,h4,fib=.60,buffer_pips=5):
    out=[]; buf=buffer_pips*pip_size(symbol)
    for i in range(2,len(h4)):
        a,b=h4.iloc[i-2],h4.iloc[i-1]
        live_start=h4.iloc[i].timestamp; live_end=live_start+pd.Timedelta(hours=4)
        if b.close>a.high:
            hi,lo=b.high,a.low; entry=hi-fib*(hi-lo); stop=lo-buf; target=hi
            risk=entry-stop; reward=target-entry
            if risk>0: out.append(Order(symbol,"bullish",b.timestamp,live_start,live_end,entry,stop,target,reward/risk))
        elif b.close<a.low:
            hi,lo=a.high,b.low; entry=lo+fib*(hi-lo); stop=hi+buf; target=lo
            risk=stop-entry; reward=entry-target
            if risk>0: out.append(Order(symbol,"bearish",b.timestamp,live_start,live_end,entry,stop,target,reward/risk))
    return out

def simulate(order,m1):
    live=m1[(m1.timestamp>=order.live_start)&(m1.timestamp<order.live_end)]
    fill=None
    for _,bar in live.iterrows():
        if bar.low<=order.entry<=bar.high:
            fill=bar.timestamp; break
    if fill is None:
        return {"status":"expired","fill_time":None,"exit_time":None,"result_r":0.0}
    after=m1[m1.timestamp>=fill]
    for _,bar in after.iterrows():
        if order.direction=="bullish":
            sl=bar.low<=order.stop; tp=bar.high>=order.target
        else:
            sl=bar.high>=order.stop; tp=bar.low<=order.target
        if sl and tp:
            return {"status":"loss_ambiguous","fill_time":fill,"exit_time":bar.timestamp,"result_r":-1.0}
        if sl: return {"status":"loss","fill_time":fill,"exit_time":bar.timestamp,"result_r":-1.0}
        if tp: return {"status":"win","fill_time":fill,"exit_time":bar.timestamp,"result_r":order.rr}
    return {"status":"open","fill_time":fill,"exit_time":None,"result_r":0.0}
