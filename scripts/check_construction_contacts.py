from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];u=json.loads((R/'data/complete_sequence_units.json').read_text());ss=json.loads((R/'data/complete_sequence_states.json').read_text());report=[];eps=1e-8
for state in ss:
 active=[v for v in u if state['states'][v['id']]!='free'];adj={v['id']:set() for v in active};contacts=0
 for i,a in enumerate(active):
  for b in active[i+1:]:
   overlap=[min(a[d]+a['d'+d],b[d]+b['d'+d])-max(a[d],b[d]) for d in ['x','y','z']]
   assert not all(d>eps for d in overlap),(state['stage'],a['id'],b['id'])
   if sum(abs(d)<=eps for d in overlap)==1 and sum(d>eps for d in overlap)==2:
    adj[a['id']].add(b['id']);adj[b['id']].add(a['id']);contacts+=1
 seeds={v['id'] for v in active if v['role']=='floor'};seen=set(seeds);todo=list(seeds)
 while todo:
  n=todo.pop()
  for m in adj[n]-seen:seen.add(m);todo.append(m)
 assert len(seen)==len(active)
 report.append(dict(stage=state['stage'],active_units=len(active),interpenetrating_pairs=0,positive_area_face_contacts=contacts,units_geometrically_connected_to_ground_mat=len(seen)))
(R/'data/construction_contact_checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
