import argparse,json
from pathlib import Path
import pandas as pd
from .engine import to_h4,setups_from_h4,simulate
from .metrics import summarize

def main():
 p=argparse.ArgumentParser();p.add_argument("--data-dir",default="data");p.add_argument("--out-dir",default="results");p.add_argument("--buffer-pips",type=float,default=None);p.add_argument("--tp-mode",choices=["live1","fixed"],default="fixed");p.add_argument("--rr",type=float,default=2.0);a=p.parse_args();cfg=json.loads(Path("config.json").read_text());rows=[]
 buffer=cfg["stop_buffer_pips"] if a.buffer_pips is None else a.buffer_pips
 for s in cfg["pairs"]:
  path=Path(a.data_dir)/f"{s}.csv"
  if not path.exists():raise FileNotFoundError(path)
  m=pd.read_csv(path);m["timestamp"]=pd.to_datetime(m["timestamp"],unit="ms",utc=True);m=m.sort_values("timestamp");ss=setups_from_h4(s,to_h4(m),buffer)
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
   rows.append({**x.__dict__,**simulate(x,m,a.tp_mode,a.rr)})
  print(f"{s}: H4 setups={len(ss)}")
 out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True);d=pd.DataFrame(rows);d.to_csv(out/"trades.csv",index=False);o=summarize(d,cfg["risk_per_trade_pct"]);pp={s:summarize(g,cfg["risk_per_trade_pct"]) for s,g in d.groupby("symbol")};(out/"summary.json").write_text(json.dumps({"buffer_pips":buffer,"tp_mode":a.tp_mode,"rr_value":a.rr if a.tp_mode=="fixed" else None,"overall":o,"per_pair":pp},indent=2,default=str));print(json.dumps(o,indent=2))
if __name__=="__main__":main()
