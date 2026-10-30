"""Five-year housing-programme scenarios: explicit assumptions, deterministic flows."""
from pathlib import Path
import csv,json,math
R=Path(__file__).resolve().parents[1]
PARAM=dict(horizon_months=60,initial_territorial_stock=10000,initial_unmet_households=300,new_need_per_month=10,parallel_sites=120,baseline_work_months=12,handover_months=1,matched_allocation_share=.6,quality_assumption='Every counted completion passes the same declared functional and structural acceptance gates',initial_pipeline='Empty new programme at month zero; existing territorial stock is tracked separately',event_timing='Admissions, arrivals and qualified completions occur at month end; dwelling-months and unmet-household-months integrate beginning-of-month stocks')
def simulate(name,target_duration=6,gate_cap=14,allocation=.6):
 active=[];ready=[];handover=[];done=0;backlog=300.;sum_backlog=0.;rows=[];admitted=0;resident_months=0
 for month in range(1,61):
  year=(month-1)//12
  duration=12-(12-target_duration)*(year/4 if name!='baseline' else 0)
  speed=12/duration
  # End-of-month qualified handovers previously released to a one-month check/service gate.
  completions=sum(1 for release in handover if release==month);handover=[x for x in handover if x!=month]
  resident_months+=done;done+=completions
  active=[x+speed for x in active]
  newly_ready=sum(1 for w in active if w>=12-1e-9);active=[w for w in active if w<12-1e-9]
  ready.extend([month]*newly_ready)
  released=min(gate_cap,len(ready));ready=ready[released:];handover.extend([month+1]*released)
  # Release construction slots only when physical assembly work finishes.
  starts=min(gate_cap,120-len(active));active.extend([0.]*starts);admitted+=starts
  sum_backlog+=backlog;backlog=max(0.,backlog+10-allocation*completions)
  rows.append(dict(scenario=name,month=month,year=month/12,nominal_build_months=duration,work_speed=speed,starts=starts,construction_wip=len(active),handover_queue=len(ready)+len(handover),qualified_completions=completions,cumulative_completions=done,unmet_households=backlog,unmet_household_months=sum_backlog,qualified_dwelling_months=resident_months,programme_started=admitted))
 return rows
def write(name,rows):
 with (R/'data'/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def run():
 cases=[simulate('baseline'),simulate('faster_assembly'),simulate('coordinated',gate_cap=20)]
 write('territory_monthly.csv',[r for c in cases for r in c]);write('territory_annual.csv',[r for c in cases for r in c if r['month']%12==0])
 finals=[dict(scenario=c[-1]['scenario'],completions=c[-1]['cumulative_completions'],unmet_households=round(c[-1]['unmet_households'],2),unmet_household_years=round(c[-1]['unmet_household_months']/12,2),qualified_dwelling_years=round(c[-1]['qualified_dwelling_months']/12,2),end_wip=c[-1]['construction_wip'],end_handover_queue=c[-1]['handover_queue']) for c in cases]
 write('territory_summary.csv',finals)
 sensitivities=[]
 for duration in [6,8,10,12]:
  for cap in [10,14,20,24]:
   x=simulate('sensitivity',target_duration=duration,gate_cap=cap)[-1];sensitivities.append(dict(year_five_build_months=duration,gate_capacity_per_month=cap,completions_60_months=x['cumulative_completions']))
 write('capacity_sensitivity.csv',sensitivities)
 write('allocation_sensitivity.csv',[dict(allocation_share=a,scenario=name,unmet_households=simulate(name,gate_cap=cap,allocation=a)[-1]['unmet_households']) for a in [.25,.4,.6,.8,1.] for name,cap in [('baseline',14),('faster_assembly',14),('coordinated',20)]])
 write('thermal_bridge.csv',[dict(bridge_area_fraction=f,insulated_path_U_W_m2K=1/(.16/.04+.17),bridge_path_U_W_m2K=2.,effective_U_W_m2K=(1-f)/(4+.17)+f*2) for f in [0,.02,.05,.1,.15,.2]])
 engineering=dict(roof_design_assumptions={'span_m':3.6,'tributary_width_m':.6,'uniform_area_load_kN_m2':1.5,'deflection_limit_span_ratio':300},line_load_kN_m=.9,bending_moment_kNm=.9*3.6**2/8,end_reaction_kN=.9*3.6/2,deflection_limit_mm=3.6*1000/300,required_EI_N_m2=5*900*3.6**4/(384*(3.6/300)),moving_module_mass_kg=15,lever_arm_m=.6,static_lifting_torque_Nm=15*9.81*.6,lift_height_m=2.7,minimum_lift_work_J=15*9.81*2.7,insulation_U_W_m2K=1/(4+.17),effective_U_at_10_percent_bridge=.9/(4+.17)+.1*2,finance_example={'average_tied_capital_currency':75000,'annual_rate':.05,'months_saved':6,'saving_currency':75000*.05*6/12})
 assert all(r['construction_wip']<=120 for c in cases for r in c)
 for c in cases:
  for x in c:assert x['programme_started']==x['construction_wip']+x['handover_queue']+x['cumulative_completions']
 assert finals[2]['completions']>=finals[1]['completions']>=finals[0]['completions']
 (R/'data/model_parameters.json').write_text(json.dumps(PARAM,indent=2));(R/'data/engineering_examples.json').write_text(json.dumps(engineering,indent=2))
 (R/'data/results.json').write_text(json.dumps({'scenarios':finals,'engineering':engineering},indent=2));print(json.dumps(finals,indent=2));print(json.dumps(engineering,indent=2))
if __name__=='__main__':run()
