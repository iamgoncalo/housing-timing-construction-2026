from pathlib import Path
from collections import deque
import random,csv,json,statistics
R=Path(__file__).resolve().parents[1];V={(x,y) for x in range(8) for y in range(8)}
def components(removed):
 alive=V-set(removed);unseen=set(alive);out=[]
 while unseen:
  start=min(unseen);c={start};unseen.remove(start);q=deque([start])
  while q:
   x,y=q.popleft()
   for a in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
    if a in unseen:unseen.remove(a);c.add(a);q.append(a)
  out.append(c)
 assert sum(map(len,out))==len(alive)
 return out
rng=random.Random(20261030);rows=[]
for kind in ['dispersed','column_cut']:
 failures=[set(rng.sample(sorted(V),8)) for i in range(2000)] if kind=='dispersed' else [{(x,y) for y in range(8)} for x in range(8)]
 for trial,failed in enumerate(failures):
  c=components(failed);largest=max(map(len,c))/56;reference=next((len(a)/56 for a in c if (0,0) in a),0)
  rows.append(dict(pattern=kind,trial=trial,failed_nodes=8,surviving_nodes=56,components=len(c),largest_component_fraction=largest,reference_coordinator_fraction=reference,all_survivors_connected=len(c)==1))
summary=[]
for kind in ['dispersed','column_cut']:
 g=[r for r in rows if r['pattern']==kind]
 summary.append(dict(pattern=kind,cases=len(g),mean_largest_component_fraction=statistics.mean(r['largest_component_fraction'] for r in g),min_largest_component_fraction=min(r['largest_component_fraction'] for r in g),mean_reference_coordinator_fraction=statistics.mean(r['reference_coordinator_fraction'] for r in g),all_connected_fraction=statistics.mean(r['all_survivors_connected'] for r in g)))
assert all(0<=r['reference_coordinator_fraction']<=r['largest_component_fraction']<=1 for r in rows)
for name,rs in [('swarm_topology_cases.csv',rows),('swarm_topology_summary.csv',summary)]:
 with (R/'data'/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
(R/'data/swarm_topology_parameters.json').write_text(json.dumps(dict(grid=[8,8],neighbourhood='orthogonal undirected nearest neighbours',failed_nodes=8,seed=20261030,dispersed_cases=2000,column_cases=8,reference_coordinator=[0,0],interpretation='Static communication connectivity experiment; surviving components are communication opportunities, not evidence of task completion or structural stability.'),indent=2))
print(json.dumps(summary,indent=2))
