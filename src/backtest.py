import argparse,json
from pathlib import Path
import pandas as pd
from .engine import to_h4,orders_from_h4,simulate
from .metrics import summarize

def main():
    p=argparse.ArgumentParser(); p.add_argument("--data-dir",default="data"); p.add_argument("--out-dir",default="results"); a=p.parse_args()
    cfg=json.loads(Path("config.json").read_text()); rows=[]
    for symbol in cfg["pairs"]:
        path=Path(a.data_dir)/f"{symbol}.csv"
        if not path.exists(): print(f"{symbol}: missing {path}"); continue
        m1=pd.read_csv(path); m1["timestamp"]=pd.to_datetime(m1["timestamp"],utc=True); m1=m1.sort_values("timestamp")
        h4=to_h4(m1)
        for o in orders_from_h4(symbol,h4,cfg["fib_retracement"],cfg["stop_buffer_pips"]):
            r=simulate(o,m1); rows.append({**o.__dict__,**r})
        print(f"{symbol}: complete")
    out=Path(a.out_dir); out.mkdir(exist_ok=True)
    df=pd.DataFrame(rows); df.to_csv(out/"trades.csv",index=False)
    overall=summarize(df,cfg["risk_per_trade_pct"]) if len(df) else {}
    per_pair={s:summarize(g,cfg["risk_per_trade_pct"]) for s,g in df.groupby("symbol")} if len(df) else {}
    (out/"summary.json").write_text(json.dumps({"overall":overall,"per_pair":per_pair},indent=2,default=str))
    print(json.dumps(overall,indent=2))

if __name__=="__main__": main()
