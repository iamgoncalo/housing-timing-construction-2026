from pathlib import Path
import random,math,csv,json,statistics
R=Path(__file__).resolve().parents[1];P=json.loads((R/'data/complete_sequence_engineering.json').read_text());L=P['roof_strip_span_m'];M=P['roof_strip_Mmid_kNm']*1000;db=P['roof_strip_bending_deflection_mm']/1000;lim=P['selected_strip_limit_mm']/1000
SIGMA=.15;N=2000;SEED=20261030;rng=random.Random(SEED)
truth=[math.exp(math.log(.35)+rng.gauss(0,.45)) for _ in range(N)];rows=[]
def delta(k):return db+M*L/(4*k*1e6)
# Paired cases across regimes; only diagnostics differ. No movement or physical sensing is simulated.
for regime in ['independent','shared_bias','stale']:
 for trial,k in enumerate(truth):
  shift=math.log(1.35) if regime=='shared_bias' else 0
  age=2 if regime=='stale' else 0
  source=k/.6 if regime=='stale' else k
  cached=source*math.exp(shift+rng.gauss(0,SIGMA))
  # Active retest obtains current observations, retaining any shared calibration error.
  readings=[k*math.exp(shift+rng.gauss(0,SIGMA)) for _ in range(3)]
  lower=math.exp(statistics.mean(math.log(x) for x in readings)-1.645*SIGMA/math.sqrt(3))
  viable=delta(k)<=lim
  decisions={'calendar':True,'single_estimate':delta(cached)<=lim,'fresh_interval':age<=1 and delta(cached*math.exp(-1.645*SIGMA))<=lim,'active_retest':delta(lower)<=lim,'truth_reference':viable}
  for policy,release in decisions.items():rows.append(dict(regime=regime,trial=trial,policy=policy,true_joint_k_MNm_rad=k,true_deflection_mm=delta(k)*1000,criterion_met=viable,release=release,violating_release=release and not viable,withheld_viable=(not release) and viable,diagnostic_count=0 if policy=='calendar' else 3 if policy=='active_retest' else 1,observation_age=age))
def wilson(n,total):
 z=1.96;p=n/total;den=1+z*z/total;mid=(p+z*z/(2*total))/den;half=z*math.sqrt(p*(1-p)/total+z*z/(4*total*total))/den;return mid-half,mid+half
out=[]
for regime in ['independent','shared_bias','stale']:
 for policy in ['calendar','single_estimate','fresh_interval','active_retest','truth_reference']:
  v=[a for a in rows if a['regime']==regime and a['policy']==policy];bad=sum(a['violating_release'] for a in v);released=sum(a['release'] for a in v);withheld=sum(a['withheld_viable'] for a in v);lo,hi=wilson(bad,N)
  out.append(dict(regime=regime,policy=policy,trials=N,releases=released,criterion_violating_releases=bad,violating_release_fraction_all_trials=bad/N,wilson95_lower=lo,wilson95_upper=hi,withheld_viable=withheld))
# Same true distribution and criterion for every policy and observation regime.
assert len(rows)==30000
for regime in ['independent','shared_bias','stale']:
 g=[a for a in out if a['regime']==regime];assert g[-1]['criterion_violating_releases']==0
for path,items in [('release_benchmark_cases.csv',rows),('release_benchmark_summary.csv',out)]:
 with (R/'data'/path).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
(R/'data/release_benchmark_parameters.json').write_text(json.dumps(dict(seed=SEED,paired_truth_cases=N,observation_regimes=3,policies=5,total_decisions=len(rows),sigma_log_observation=SIGMA,true_k_median_MNm_rad=.35,true_k_sigma_log=.45,shared_positive_bias_multiplier=1.35,stale_current_to_recorded_multiplier=.6,stale_age=2,maximum_accepted_age=1,one_sided_normal_quantile=1.645,criterion='Selected 13 mm static deflection, exact reference strip; all other properties held fixed',interpretation='Synthetic support-release diagnostic benchmark; truth reference is an upper-information comparator, not an implementable local controller; no hardware, movement, or complete safety result.'),indent=2))
with (R/'tables/release_benchmark.tex').open('w') as f:
 f.write(r'''\begin{table}[!htbp]\centering\small
\caption{Synthetic support-release benchmark: releases violating the selected deflection criterion, per 2,000 trials. Parentheses show viable cases withheld.}\label{tab:releasebenchmark}
\begin{tabularx}{\linewidth}{@{}Yrrr@{}}\toprule
Policy & Independent & Shared bias & Stale record\\\midrule
''')
 for policy,label in [('calendar','Calendar release'),('single_estimate','Single estimate'),('fresh_interval','Freshness + interval'),('active_retest','Active retest'),('truth_reference','Truth reference')]:
  cells=[]
  for regime in ['independent','shared_bias','stale']:
   a=next(x for x in out if x['regime']==regime and x['policy']==policy);cells.append(f"{a['criterion_violating_releases']} ({a['withheld_viable']})")
  f.write(label+' & '+' & '.join(cells)+r'\\'+'\n')
 f.write(r'\bottomrule\end{tabularx}\end{table}')
print(json.dumps(out,indent=2))
