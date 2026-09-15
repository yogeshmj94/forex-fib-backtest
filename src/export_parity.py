import argparse,json
from pathlib import Path
import pandas as pd

REQUIRED=["symbol","direction","signal_time","live_start","live_end","fib60","fib80","stop","target","status","timeframe","ob_time","entry","rr","fill_time","exit_time","result_r"]

def iso(v):
    if pd.isna(v): return None
    try: return pd.Timestamp(v).isoformat()
    except Exception: return str(v)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--trades",required=True)
    p.add_argument("--out",default="parity/reference_trades.jsonl")
    p.add_argument("--statuses",default="win,loss,loss_ambiguous,expired,no_ob")
    p.add_argument("--per-symbol-status",type=int,default=2)
    a=p.parse_args()
    d=pd.read_csv(a.trades)
    missing=[x for x in REQUIRED if x not in d.columns]
    if missing: raise SystemExit(f"missing columns: {missing}")
    statuses=[x.strip() for x in a.statuses.split(",") if x.strip()]
    d=d[d.status.isin(statuses)].copy()
    d=d.sort_values(["symbol","status","signal_time","live_start"],kind="stable")
    sample=d.groupby(["symbol","status"],sort=True,group_keys=False).head(a.per_symbol_status)
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    timecols={"signal_time","live_start","live_end","ob_time","fill_time","exit_time"}
    pricecols={"fib60","fib80","stop","target","entry","rr","result_r"}
    with out.open("w") as fh:
        for _,r in sample.iterrows():
            rec={}
            for k in REQUIRED:
                v=r[k]
                if k in timecols: rec[k]=iso(v)
                elif k in pricecols: rec[k]=None if pd.isna(v) else float(v)
                else: rec[k]=None if pd.isna(v) else str(v)
            rec["fixture_version"]=1
            rec["stop_buffer_pips"]=3.0
            rec["tp_mode"]="fixed"
            rec["tp_rr"]=1.0
            fh.write(json.dumps(rec,separators=(",",":"))+"\n")
    print(f"wrote {len(sample)} parity fixtures to {out}")

if __name__=="__main__": main()
