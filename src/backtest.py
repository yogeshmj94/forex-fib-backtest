import argparse,json
from pathlib import Path
import pandas as pd
from .engine import to_h4,to_d1,setups_from_h4,simulate,pip_size
from .metrics import summarize

def d1_interaction_bucket(distance_pips):
 if distance_pips < 0: return "swept"
 if distance_pips == 0: return "exact_touch"
 if distance_pips <= 5: return "above_0_5"
 if distance_pips <= 10: return "above_5_10"
 if distance_pips <= 20: return "above_10_20"
 return "above_20"

def main():
 p=argparse.ArgumentParser();p.add_argument("--data-dir",default="data");p.add_argument("--out-dir",default="results");p.add_argument("--buffer-pips",type=float,default=None);p.add_argument("--tp-mode",choices=["live1","fixed"],default="fixed");p.add_argument("--rr",type=float,default=2.0);a=p.parse_args();cfg=json.loads(Path("config.json").read_text());rows=[]
 buffer=cfg["stop_buffer_pips"] if a.buffer_pips is None else a.buffer_pips
 for s in cfg["pairs"]:
  path=Path(a.data_dir)/f"{s}.csv"
  if not path.exists():raise FileNotFoundError(path)
  m=pd.read_csv(path);m["timestamp"]=pd.to_datetime(m["timestamp"],unit="ms",utc=True);m=m.sort_values("timestamp");h=to_h4(m);d1=to_d1(m);ss=setups_from_h4(s,h,buffer)
  h_by_time=h.set_index("timestamp")
  d1_by_time=d1.set_index("timestamp")
  for x in ss:
   # Match the live scanner: Monday-Friday and Live H4 overlaps either
   # London 08:00-17:00 Europe/London or New York 08:00-17:00 America/New_York.
   st=x.live_start
   if st.weekday()>=5: continue
   en=x.live_end
   lon_st=st.tz_convert("Europe/London"); lon_en=en.tz_convert("Europe/London")
   ny_st=st.tz_convert("America/New_York"); ny_en=en.tz_convert("America/New_York")
   london=(lon_st.hour < 17 and (lon_en.hour > 8 or lon_en.date()!=lon_st.date()))
   newyork=(ny_st.hour < 17 and (ny_en.hour > 8 or ny_en.date()!=ny_st.date()))
   if not (london or newyork): continue
   pos=h_by_time.index.get_indexer([x.signal_time])[0]
   if pos <= 0: continue
   live1=h_by_time.iloc[pos];live2=h_by_time.iloc[pos-1]
   ps=pip_size(s)
   if x.direction=="bullish":
    impulse_pips=(live1.high-live2.low)/ps
    breakout_pips=(live1.close-live2.high)/ps
   else:
    impulse_pips=(live2.high-live1.low)/ps
    breakout_pips=(live2.low-live1.close)/ps
   momentum_pct=(breakout_pips/impulse_pips*100.0) if impulse_pips>0 else None

   # Live-1 D1 is the most recent fully completed UTC daily candle before the
   # current Live H4 day. Never use the still-forming current D1 candle.
   live_day=x.live_start.floor("D")
   prior_d1=d1_by_time[d1_by_time.index < live_day]
   if prior_d1.empty: continue
   live1_d1=prior_d1.iloc[-1]
   if x.direction=="bullish":
    d1_target=live1_d1.high
    htf_room_pips=(d1_target-live1.high)/ps
    htf_valid=d1_target>live1.high
    # Signed support distance: negative means Live-2 H4 swept below Live-1 D1 low.
    d1_proximity_pips=(live2.low-live1_d1.low)/ps
    d1_reclaimed=live2.low<live1_d1.low and live2.close>live1_d1.low
   else:
    d1_target=live1_d1.low
    htf_room_pips=(live1.low-d1_target)/ps
    htf_valid=d1_target<live1.low
    # Mirrored resistance distance: negative means Live-2 H4 swept above Live-1 D1 high.
    d1_proximity_pips=(live1_d1.high-live2.high)/ps
    d1_reclaimed=live2.high>live1_d1.high and live2.close<live1_d1.high
   d1_bucket=d1_interaction_bucket(d1_proximity_pips)
   d1_swept=d1_proximity_pips<0
   structural_room_pct=(htf_room_pips/impulse_pips*100.0) if impulse_pips>0 else None
   diag={"live2_low":live2.low,"live2_high":live2.high,"live2_close":live2.close,"live1_open":live1.open,"live1_high":live1.high,"live1_low":live1.low,"live1_close":live1.close,"impulse_pips":impulse_pips,"breakout_pips":breakout_pips,"momentum_pct":momentum_pct,"live1_d1_high":live1_d1.high,"live1_d1_low":live1_d1.low,"d1_target":d1_target,"htf_room_pips":htf_room_pips,"structural_room_pct":structural_room_pct,"htf_valid":htf_valid,"live2_d1_proximity_pips":d1_proximity_pips,"live2_d1_interaction":d1_bucket,"live2_d1_swept":d1_swept,"live2_d1_reclaimed":d1_reclaimed}
   if not htf_valid:
    rows.append({**x.__dict__,**diag,"status":"invalid_htf_structure","timeframe":None,"ob_time":None,"entry":None,"rr":None,"fill_time":None,"exit_time":None,"result_r":0.})
    continue
   # For this hypothesis the completed Live-1 D1 extreme replaces the H4
   # extreme as the structural target. Equality is invalidated above because
   # there is no usable room after allowing for spread/liquidity sweep.
   x.target=d1_target
   rows.append({**x.__dict__,**diag,**simulate(x,m,a.tp_mode,a.rr)})
  print(f"{s}: H4 setups={len(ss)}")
 out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True);d=pd.DataFrame(rows);d.to_csv(out/"trades.csv",index=False);o=summarize(d,cfg["risk_per_trade_pct"]);pp={s:summarize(g,cfg["risk_per_trade_pct"]) for s,g in d.groupby("symbol")};(out/"summary.json").write_text(json.dumps({"buffer_pips":buffer,"tp_mode":a.tp_mode,"rr_value":a.rr if a.tp_mode=="fixed" else None,"structural_target":"completed_live1_d1_extreme","overall":o,"per_pair":pp},indent=2,default=str));print(json.dumps(o,indent=2))
if __name__=="__main__":main()
