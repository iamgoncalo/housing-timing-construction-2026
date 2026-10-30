"""Independent checks: finite elements, closed-form valuation, union-find and cohort accounting."""
from pathlib import Path
import csv,json,math,random,collections
import numpy as np
R=Path(__file__).resolve().parents[1];checks={}
def beam(nodes,EI,w,k=None):
 # Separate rotations on either side of the central contact; shared vertical displacement.
 mid=nodes.index((nodes[0]+nodes[-1])/2);nd=2*len(nodes)+(k is not None);K=np.zeros((nd,nd));F=np.zeros(nd)
 for i in range(len(nodes)-1):
  l=nodes[i+1]-nodes[i];ix=[2*i,2*i+1,2*i+2,2*i+3]
  if k is not None and i==mid:ix[1]=nd-1
  ke=EI/l**3*np.array([[12,6*l,-12,6*l],[6*l,4*l*l,-6*l,2*l*l],[-12,-6*l,12,-6*l],[6*l,2*l*l,-6*l,4*l*l]])
  fe=w*l/2*np.array([1,l/6,1,-l/6]);K[np.ix_(ix,ix)]+=ke;F[ix]+=fe
 if k is not None:
  ix=[2*mid+1,nd-1];K[np.ix_(ix,ix)]+=k*np.array([[1,-1],[-1,1]])
 supports=[0,2*(len(nodes)-1)] if len(nodes)==3 else [2,2*(len(nodes)-2)]
 free=[x for x in range(nd) if x not in supports];u=np.zeros(nd);u[free]=np.linalg.solve(K[np.ix_(free,free)],F[free]);return u[2*mid],(K@u-F)[supports]
errors=[]
for row in csv.DictReader((R/'data/connection_sensitivity.csv').open()):
 w=float(row['q_kN_m2'])*3600+15/.6*9.81;k=None if row['k_MNm_rad']=='rigid' else float(row['k_MNm_rad'])*1e6
 d,_=beam([0,1.8,3.6],float(row['EI_MNm2'])*1e6,w,k);errors.append(abs(d*1000-float(row['total_deflection_mm'])))
assert max(errors)<1e-8;checks['63_spring_cases_finite_elements_max_mm_error']=max(errors)
p=json.loads((R/'data/complete_sequence_engineering.json').read_text());d,reactions=beam([0,.15,2.1,4.05,4.2],.25e6,695.25)
assert abs(d*1000-p['roof_strip_bending_deflection_mm'])<1e-8
assert max(abs(abs(x)/1000-p['roof_strip_end_reaction_kN']) for x in reactions)<1e-8
d,_=beam([0,.15,2.1,4.05,4.2],.25e6,695.25,p['minimum_selected_central_k_MNm_rad']*1e6);assert abs(d-.013)<1e-10
checks['whole_roof_strip_finite_elements']='Deflection, equilibrium reactions and spring threshold agree'
ve=[]
for row in csv.DictReader((R/'data/valuation_timing.csv').open()):
 r=float(row['annual_discount_rate']);h=float(row['annual_claim_extinguishment_hazard']);d=int(row['months_before_service']);a=((1-h)/(1+r))**(1/12)
 closed=750*a**(d+1)*(1-a**(60-d))/(1-a)+150000*a**60;ve.append(abs(closed-float(row['total_PV_currency'])))
assert max(ve)<1e-8;checks['45_valuations_geometric_series_max_currency_error']=max(ve)
# Union-find is independent of the published breadth-first component traversal.
rng=random.Random(20261030);V=[(x,y) for x in range(8) for y in range(8)];saved=list(csv.DictReader((R/'data/swarm_topology_cases.csv').open()))
for row in saved:
 removed=set(rng.sample(V,8)) if row['pattern']=='dispersed' else {(int(row['trial']),y) for y in range(8)}
 live=set(V)-removed;parent={x:x for x in live}
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 for x,y in live:
  for v in [(x+1,y),(x,y+1)]:
   if v in live:parent[find((x,y))]=find(v)
 counts=collections.Counter(find(v) for v in live)
 assert len(counts)==int(row['components']) and abs(max(counts.values())/56-float(row['largest_component_fraction']))<1e-12
 ref=counts[find((0,0))]/56 if (0,0) in live else 0;assert abs(ref-float(row['reference_coordinator_fraction']))<1e-12
checks['2008_topology_cases_union_find']='All component and reference-reachability records agree'
# Rebuild delivery with cohorts and remaining work, not individual cumulative work counters.
for scenario,cap in [('baseline',14),('faster_assembly',14),('coordinated',20)]:
 cohorts=[];queue=0;next_handover=0;total=0;resident=0;backlog=300.;area=0
 saved=list(csv.DictReader((R/'data/territory_monthly.csv').open()));saved=[x for x in saved if x['scenario']==scenario]
 for month in range(1,61):
  completed=next_handover;resident+=total;total+=completed;speed=1 if scenario=='baseline' else 12/(12-1.5*((month-1)//12))
  new=[]
  for count,remaining in cohorts:
   remaining-=speed
   if remaining<=1e-9:queue+=count
   else:new.append((count,remaining))
  next_handover=min(cap,queue);queue-=next_handover;starts=min(cap,120-sum(n for n,_ in new));cohorts=new+[(starts,12.)];area+=backlog;backlog=max(0,backlog+10-.6*completed)
  row=saved[month-1]
  assert total==int(row['cumulative_completions']) and resident==int(row['qualified_dwelling_months'])
  assert abs(backlog-float(row['unmet_households']))<1e-8 and abs(area-float(row['unmet_household_months']))<1e-8
checks['180_territorial_months_independent_cohorts']='All monthly completions, dwelling-months and unmet-household records agree'
# Re-evaluate every saved diagnostic decision against the closed-form spring threshold.
threshold=p['minimum_selected_central_k_MNm_rad'];groups=collections.defaultdict(list)
for x in csv.DictReader((R/'data/release_benchmark_cases.csv').open()):
 viable=float(x['true_joint_k_MNm_rad'])>=threshold;release=x['release']=='True'
 assert viable==(x['criterion_met']=='True') and (release and not viable)==(x['violating_release']=='True')
 assert ((not release) and viable)==(x['withheld_viable']=='True');groups[(x['regime'],x['policy'])].append(x)
for x in csv.DictReader((R/'data/release_benchmark_summary.csv').open()):
 g=groups[(x['regime'],x['policy'])];assert sum(v['violating_release']=='True' for v in g)==int(x['criterion_violating_releases'])
 assert sum(v['withheld_viable']=='True' for v in g)==int(x['withheld_viable'])
checks['30000_decisions_independent_threshold_and_recount']='All true criterion labels and decision-error totals agree; observation-policy implementation separately inspected'
checks['gravity_and_thermal']=dict(torque_Nm=15*9.81*.6,lift_J=15*9.81*2.7,insulated_U=1/(.17+.16/.04),bridged_U=.9/(.17+.16/.04)+.1*2)
(R/'verification').mkdir(exist_ok=True)
(R/'verification/final_independent_calculations.json').write_text(json.dumps(dict(passed=True,checks=checks,limitations='Verification of declared numerical models; no physical validation or regulatory certification.'),indent=2));print(json.dumps(checks,indent=2))
