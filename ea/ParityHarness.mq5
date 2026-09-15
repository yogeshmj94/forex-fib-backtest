#property script_show_inputs
#include "ForexFibSignal.mqh"

input string FixtureFile="reference_trades.jsonl";
input double PriceTolerancePoints=1.0;

string ExtractString(string line,string key)
{
 string needle="\""+key+"\":\"";int p=StringFind(line,needle);
 if(p<0)return "";p+=StringLen(needle);int e=StringFind(line,"\"",p);
 return e<0?"":StringSubstr(line,p,e-p);
}
double ExtractNumber(string line,string key,double fallback=EMPTY_VALUE)
{
 string needle="\""+key+"\":";int p=StringFind(line,needle);
 if(p<0)return fallback;p+=StringLen(needle);
 while(p<StringLen(line) && StringGetCharacter(line,p)==' ')p++;
 if(StringSubstr(line,p,4)=="null")return fallback;
 int e=p;while(e<StringLen(line)){
   ushort ch=StringGetCharacter(line,e);
   if(ch==',' || ch=='}')break;e++;
 }
 return StringToDouble(StringSubstr(line,p,e-p));
}
datetime ParseISO(string s)
{
 if(s=="")return 0;StringReplace(s,"T"," ");StringReplace(s,"+00:00","");
 int dot=StringFind(s,".");if(dot>=0)s=StringSubstr(s,0,dot);
 return StringToTime(s);
}
bool Near(double a,double b,string symbol)
{
 if(a==EMPTY_VALUE && b==EMPTY_VALUE)return true;
 if(a==EMPTY_VALUE || b==EMPTY_VALUE)return false;
 return MathAbs(a-b)<=PriceTolerancePoints*SymbolInfoDouble(symbol,SYMBOL_POINT)+1e-12;
}
void OnStart()
{
 int h=FileOpen(FixtureFile,FILE_READ|FILE_TXT|FILE_ANSI);
 if(h==INVALID_HANDLE){Print("PARITY ERROR: cannot open ",FixtureFile," code=",GetLastError());return;}
 int total=0,setupPass=0,obPass=0,lifePass=0;
 while(!FileIsEnding(h)){
   string line=FileReadString(h);if(StringLen(line)<10)continue;total++;
   string symbol=ExtractString(line,"symbol"),dir=ExtractString(line,"direction");
   datetime signal=ParseISO(ExtractString(line,"signal_time"));
   datetime liveStart=ParseISO(ExtractString(line,"live_start"));
   double expFib60=ExtractNumber(line,"fib60"),expFib80=ExtractNumber(line,"fib80");
   double expEntry=ExtractNumber(line,"entry");
   string expStatus=ExtractString(line,"status");
   MqlRates h4[];ArraySetAsSeries(h4,false);
   int n=CopyRates(symbol,PERIOD_H4,signal-4*60*60,signal+4*60*60-1,h4);
   if(n<2){Print("PARITY FAIL bars ",symbol," ",TimeToString(signal));continue;}
   MqlRates a=h4[0],b=h4[1];FrozenSetup x;
   bool made=BuildSetup(symbol,a,b,liveStart,StopBufferPips,x);
   SignalDirection expected=dir=="bullish"?DIR_BULL:DIR_BEAR;
   bool sOK=made && x.direction==expected && Near(x.fib60,expFib60,symbol) && Near(x.fib80,expFib80,symbol);
   if(sOK)setupPass++; else {Print("PARITY FAIL setup ",symbol," ",TimeToString(signal));continue;}
   FrozenOB ob;ob.found=false;bool found=FindFrozenOB(x,ob);
   bool expectedOB=expEntry!=EMPTY_VALUE;
   bool oOK=(found==expectedOB) && (!found || Near(ob.entry,expEntry,symbol));
   if(oOK)obPass++; else {Print("PARITY FAIL ob ",symbol," ",TimeToString(signal));continue;}
   if(!found){lifePass++;continue;}
   // Lifecycle parity is run only when enough M1 history is available locally.
   datetime end=ParseISO(ExtractString(line,"exit_time"));if(end==0)end=x.live_end;
   MqlRates m1[];ArraySetAsSeries(m1,false);
   int m=CopyRates(symbol,PERIOD_M1,x.live_start,end+60,m1);
   if(m<=0){Print("PARITY SKIP lifecycle history ",symbol);continue;}
   SimResult sr;if(!SimulateFrozenLifecycle(x,ob,m1,sr))continue;
   string got=sr.status==SIM_WIN?"win":sr.status==SIM_LOSS?"loss":sr.status==SIM_LOSS_AMBIGUOUS?"loss_ambiguous":sr.status==SIM_EXPIRED?"expired":"open";
   if(got==expStatus)lifePass++;else Print("PARITY FAIL lifecycle ",symbol," expected=",expStatus," got=",got);
 }
 FileClose(h);
 Print("PARITY REPORT total=",total," setup=",setupPass," ob=",obPass," lifecycle=",lifePass);
 Print("Trading must remain disabled until all applicable fixture checks pass.");
}
