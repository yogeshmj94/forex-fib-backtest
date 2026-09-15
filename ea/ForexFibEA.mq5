#property strict
#property version   "0.1"
#property description "Frozen forex-fib strategy execution shell. Signal parity must be validated before live use."

#include <Trade/Trade.mqh>
CTrade trade;

input double InitialAccountBalance = 0.0;
input double RiskPercent = 0.20;
input double StopBufferPips = 3.0;
input double TakeProfitR = 1.0;
input long   MagicNumber = 26091501;
input int    MaxOpenPositions = 8;
input double MaxNominalOpenRiskPct = 1.60;
input bool   EnableTrading = false;

double ReferenceBalance()
{
   return InitialAccountBalance > 0.0 ? InitialAccountBalance : AccountInfoDouble(ACCOUNT_BALANCE);
}

double PipSize(const string symbol)
{
   int digits=(int)SymbolInfoInteger(symbol,SYMBOL_DIGITS);
   double point=SymbolInfoDouble(symbol,SYMBOL_POINT);
   return (digits==3 || digits==5) ? point*10.0 : point;
}

double NormalizeVolume(const string symbol,double volume)
{
   double minv=SymbolInfoDouble(symbol,SYMBOL_VOLUME_MIN);
   double maxv=SymbolInfoDouble(symbol,SYMBOL_VOLUME_MAX);
   double step=SymbolInfoDouble(symbol,SYMBOL_VOLUME_STEP);
   if(step<=0) return 0;
   volume=MathMax(minv,MathMin(maxv,volume));
   volume=MathFloor(volume/step+1e-9)*step;
   return NormalizeDouble(volume,8);
}

double LotsForFixedRisk(const string symbol,const double entry,const double stop)
{
   double riskMoney=ReferenceBalance()*(RiskPercent/100.0);
   double tickSize=SymbolInfoDouble(symbol,SYMBOL_TRADE_TICK_SIZE);
   double tickValue=SymbolInfoDouble(symbol,SYMBOL_TRADE_TICK_VALUE_LOSS);
   double distance=MathAbs(entry-stop);
   if(riskMoney<=0 || tickSize<=0 || tickValue<=0 || distance<=0) return 0;
   double lossPerLot=(distance/tickSize)*tickValue;
   return NormalizeVolume(symbol,riskMoney/lossPerLot);
}

int StrategyOpenPositions()
{
   int count=0;
   for(int i=0;i<PositionsTotal();i++)
   {
      ulong ticket=PositionGetTicket(i);
      if(ticket && PositionSelectByTicket(ticket) &&
         PositionGetInteger(POSITION_MAGIC)==MagicNumber) count++;
   }
   return count;
}

bool PortfolioGuard()
{
   int n=StrategyOpenPositions();
   if(n>=MaxOpenPositions) return false;
   if((n+1)*RiskPercent>MaxNominalOpenRiskPct+1e-9) return false;
   return true;
}

// This function is deliberately the only route to an order.
// The signal engine will call it only after Python-vs-MQL parity tests pass.
bool PlaceFrozenOrder(const string symbol,const ENUM_ORDER_TYPE type,
                      const double requestedEntry,const double structuralStop)
{
   if(!EnableTrading || !PortfolioGuard()) return false;
   double pip=PipSize(symbol);
   double stop=(type==ORDER_TYPE_BUY_LIMIT)
      ? structuralStop-StopBufferPips*pip
      : structuralStop+StopBufferPips*pip;
   double risk=MathAbs(requestedEntry-stop);
   if(risk<=0) return false;
   double tp=(type==ORDER_TYPE_BUY_LIMIT)
      ? requestedEntry+TakeProfitR*risk
      : requestedEntry-TakeProfitR*risk;
   double lots=LotsForFixedRisk(symbol,requestedEntry,stop);
   if(lots<=0) return false;

   trade.SetExpertMagicNumber(MagicNumber);
   trade.SetTypeFillingBySymbol(symbol);
   if(type==ORDER_TYPE_BUY_LIMIT)
      return trade.BuyLimit(lots,requestedEntry,symbol,stop,tp,ORDER_TIME_GTC,0,"fib-frozen-v1");
   if(type==ORDER_TYPE_SELL_LIMIT)
      return trade.SellLimit(lots,requestedEntry,symbol,stop,tp,ORDER_TIME_GTC,0,"fib-frozen-v1");
   return false;
}

int OnInit()
{
   if(MathAbs(RiskPercent-0.20)>1e-9 || MathAbs(StopBufferPips-3.0)>1e-9 ||
      MathAbs(TakeProfitR-1.0)>1e-9)
      Print("WARNING: inputs differ from frozen research configuration.");
   Print("ForexFibEA v0.1 loaded. Trading=",EnableTrading,
         ". Signal engine intentionally disabled until parity validation.");
   return INIT_SUCCEEDED;
}

void OnTick()
{
   // No autonomous entries in v0.1. We do not translate the visual/MTF signal
   // logic into live orders until deterministic parity fixtures are in place.
}
