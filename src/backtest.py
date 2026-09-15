import argparse,json
from pathlib import Path
import pandas as pd
from .engine import to_h4,setups_from_h4,simulate
from .metrics import summarize
def main():
 p=argparse.ArgumentParser();p.add_argument("--data-dir",default="data");p.add_argument("--out-dir",default="results");a=p.parse_args();cfg=json.loads(Path("config.json").read_text());rows=[]
 for s in cfg["pairs"]:
  path=Path(a.data_dir)/f"{s}.csv"
  if not path.exists():raise FileNotFoundError(path)
  m=pd.read_csv(path);m["timestamp"]=pd.to_datetime(m["timestamp"],unit="ms",utc=True);m=m.sort_values("timestamp");ss=setups_from_h4(s,to_h4(m),cfg["stop_buffer_pips"])
  for x in ss:rows.append({**x.__dict__,**simulate(x,m)})
  print(f"{s}: H4 setups={len(ss)}")
 out=Path(a.out_dir);out.mkdir(exist_ok=True);d=pd.DataFrame(rows);d.to_csv(out/"trades.csv",index=False);o=summarize(d,cfg["risk_per_trade_pct"]);pp={s:summarize(g,cfg["risk_per_trade_pct"]) for s,g in d.groupby("symbol")};(out/"summary.json").write_text(json.dumps({"overall":o,"per_pair":pp},indent=2,default=str));print(json.dumps(o,indent=2))
if __name__=="__main__":main()
