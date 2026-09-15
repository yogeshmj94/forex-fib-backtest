#ifndef FOREX_FIB_SIGNAL_MQH
#define FOREX_FIB_SIGNAL_MQH

enum SignalDirection { DIR_NONE=0, DIR_BULL=1, DIR_BEAR=-1 };
struct FrozenSetup {
 string symbol; SignalDirection direction; datetime signal_time,live_start,live_end;
 double fib60,fib80,structural_stop,target;
};
struct FrozenOB { bool found; ENUM_TIMEFRAMES tf; datetime time; double entry; };

double BarOpen(const MqlRates &r){return r.open;}
bool Opposite(const MqlRates &r,SignalDirection d){
 return d==DIR_BULL ? r.close<r.open : r.close>r.open;
}

// Mirrors Python setups_from_h4(): a=Live-2, b=Live-1, current bar is Live.
// IMPORTANT: pass only CLOSED H4 bars for a and b.
bool BuildSetup(const string symbol,const MqlRates &a,const MqlRates &b,
                const datetime live_start,const double buffer_pips,FrozenSetup &x)
{
 double pip=PipSize(symbol);
 x.symbol=symbol;x.signal_time=b.time;x.live_start=live_start;x.live_end=live_start+4*60*60;
 if(b.close>a.high){
   x.direction=DIR_BULL; double hi=b.high,lo=a.low;
   x.fib60=hi-.6*(hi-lo);x.fib80=hi-.8*(hi-lo);
   x.structural_stop=lo; x.target=hi; return true;
 }
 if(b.close<a.low){
   x.direction=DIR_BEAR; double hi=a.high,lo=b.low;
   x.fib60=lo+.6*(hi-lo);x.fib80=lo+.8*(hi-lo);
   x.structural_stop=hi; x.target=lo; return true;
 }
 x.direction=DIR_NONE; return false;
}

int LastSunday(int year,int month)
{
 MqlDateTime d;d.year=year;d.mon=month+1;d.day=1;d.hour=0;d.min=0;d.sec=0;
 if(month==12){d.year=year+1;d.mon=1;}
 datetime firstNext=StructToTime(d);
 datetime last=firstNext-24*60*60;MqlDateTime x;TimeToStruct(last,x);
 return x.day-x.day_of_week;
}
int NthSunday(int year,int month,int nth)
{
 MqlDateTime d;d.year=year;d.mon=month;d.day=1;d.hour=0;d.min=0;d.sec=0;
 datetime first=StructToTime(d);MqlDateTime x;TimeToStruct(first,x);
 int firstSunday=1+((7-x.day_of_week)%7);return firstSunday+7*(nth-1);
}
bool LondonDST(datetime utc)
{
 MqlDateTime x;TimeToStruct(utc,x);
 MqlDateTime s=x,e=x;s.mon=3;s.day=LastSunday(x.year,3);s.hour=1;s.min=0;s.sec=0;
 e.mon=10;e.day=LastSunday(x.year,10);e.hour=1;e.min=0;e.sec=0;
 return utc>=StructToTime(s) && utc<StructToTime(e);
}
bool NewYorkDST(datetime utc)
{
 MqlDateTime x;TimeToStruct(utc,x);
 MqlDateTime s=x,e=x;s.mon=3;s.day=NthSunday(x.year,3,2);s.hour=7;s.min=0;s.sec=0;
 e.mon=11;e.day=NthSunday(x.year,11,1);e.hour=6;e.min=0;e.sec=0;
 return utc>=StructToTime(s) && utc<StructToTime(e);
}
bool WindowOverlapsLocalSession(datetime utcStart,int utcOffsetHours)
{
 datetime localStart=utcStart+utcOffsetHours*60*60,localEnd=localStart+4*60*60;
 MqlDateTime a,b;TimeToStruct(localStart,a);TimeToStruct(localEnd,b);
 return a.hour<17 && (b.hour>8 || b.day!=a.day);
}
bool SessionEligibleUTC(const datetime live_start)
{
 MqlDateTime t;TimeToStruct(live_start,t);
 if(t.day_of_week==0 || t.day_of_week==6) return false;
 int londonOffset=LondonDST(live_start)?1:0;
 int nyOffset=NewYorkDST(live_start)?-4:-5;
 return WindowOverlapsLocalSession(live_start,londonOffset) ||
        WindowOverlapsLocalSession(live_start,nyOffset);
}

bool FindOBInRates(const FrozenSetup &x,const MqlRates &rates[],FrozenOB &ob)
{
 double zlo=MathMin(x.fib60,x.fib80),zhi=MathMax(x.fib60,x.fib80);
 int n=ArraySize(rates);
 for(int j=1;j<n;j++){
   bool crossed=x.direction==DIR_BULL ? rates[j].high>=x.fib60 : rates[j].low<=x.fib60;
   if(!crossed) continue;
   for(int k=j-1;k>=0;k--){
     if(!Opposite(rates[k],x.direction)) continue;
     double entry=x.direction==DIR_BULL ? rates[k].low : rates[k].high;
     if(entry>=zlo && entry<=zhi){ob.found=true;ob.time=rates[k].time;ob.entry=entry;return true;}
   }
   break;
 }
 return false;
}

// Python priority is M15 -> M5 -> M3 -> M2 -> M1.
// Caller supplies bars restricted to [signal_time-4h, live_start).
bool FindFrozenOB(const FrozenSetup &x,FrozenOB &ob)
{
 ENUM_TIMEFRAMES tfs[5]={PERIOD_M15,PERIOD_M5,PERIOD_M3,PERIOD_M2,PERIOD_M1};
 datetime from=x.signal_time-4*60*60,to=x.live_start-1;
 for(int i=0;i<5;i++){
   MqlRates r[];ArraySetAsSeries(r,false);
   int copied=CopyRates(x.symbol,tfs[i],from,to,r);
   if(copied<=1) continue;
   FrozenOB candidate;candidate.found=false;candidate.tf=tfs[i];
   if(FindOBInRates(x,r,candidate)){ob=candidate;return true;}
 }
 ob.found=false;return false;
}
#endif
