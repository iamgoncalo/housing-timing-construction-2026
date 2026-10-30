from pathlib import Path
import csv,json
R=Path(__file__).resolve().parents[1];T=60;flow=750.;terminal=150000.
def value(rate,delay,hazard=0):
 benefits=sum(flow*(1-hazard)**(t/12)/(1+rate)**(t/12) for t in range(delay+1,T+1))
 residual=terminal*(1-hazard)**(T/12)/(1+rate)**(T/12)
 return benefits,residual,benefits+residual
rows=[]
for r in [.04,.08,.12]:
 for d in [0,6,12,24,36]:
  for h in [0,.02,.05]:
   f,v,p=value(r,d,h);rows.append(dict(annual_discount_rate=r,months_before_service=d,annual_claim_extinguishment_hazard=h,service_PV_currency=f,terminal_PV_currency=v,total_PV_currency=p))
with (R/'data/valuation_timing.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
assert len(rows)==45
for r in [.04,.08,.12]:
 vals=[value(r,d)[2] for d in [0,6,12,24,36]];assert all(a>b for a,b in zip(vals,vals[1:]))
for d in [0,6,12,24,36]:assert value(.04,d)[2]>value(.08,d)[2]>value(.12,d)[2]
summary=dict(cases=45,horizon_months=T,net_monthly_service_flow_currency=flow,terminal_ex_dividend_claim_value_currency=terminal,base_discount_rate=.08,base_immediate=value(.08,0),base_delay_12=value(.08,12),base_delay_36=value(.08,36),base_hazard_05=value(.08,0,.05),interpretation='Selected-input finite-horizon present value of one specified residential claim. Use-flow is net rent OR imputed service; common ex-dividend terminal payoff covers post-horizon value. Not a market estimate or a construction-cost forecast.')
(R/'data/valuation_timing_parameters.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
