from pathlib import Path
import csv,json,math
R=Path(__file__).resolve().parents[1];L=3.6;unit_mass=15.;pitch=.6;g=9.81
rows=[]
for q in [1.,1.5,2.]:
 for EI in [2.1e6,2.9e6,3.7e6]:
  w=q*3.6+unit_mass/pitch*g/1000;M=w*1000*L**2/8;db=5*w*1000*L**4/(384*EI);limit=L/300
  for k in [.1e6,.25e6,.5e6,1e6,2e6,5e6,math.inf]:
   dj=0 if math.isinf(k) else M*L/(4*k)
   rows.append(dict(q_kN_m2=q,EI_MNm2=EI/1e6,k_MNm_rad='rigid' if math.isinf(k) else k/1e6,beam_deflection_mm=db*1000,joint_deflection_mm=dj*1000,total_deflection_mm=(db+dj)*1000,selected_limit_mm=limit*1000,within_selected_limit=db+dj<=limit))
with (R/'data/connection_sensitivity.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
base=[r for r in rows if r['q_kN_m2']==1.5 and r['EI_MNm2']==2.9];M=(1.5*3.6+unit_mass/pitch*g/1000)*1000*L**2/8;kreq=M*L/(4*(.012-base[0]['beam_deflection_mm']/1000))
assert len(rows)==63
for q in [1.,1.5,2.]:
 for EI in [2.1,2.9,3.7]:
  vals=[r['total_deflection_mm'] for r in rows if r['q_kN_m2']==q and r['EI_MNm2']==EI];assert all(a>=b for a,b in zip(vals,vals[1:]))
result=dict(cases=63,base=base,span_m=L,module_pitch_m=pitch,moving_mass_input_kg=unit_mass,assembled_effective_EI_input_MNm2=2.9,base_line_load_kN_m=1.5*3.6+unit_mass/pitch*g/1000,base_moment_kNm=M/1000,base_reaction_kN=(1.5*3.6+unit_mass/pitch*g/1000)*L/2,required_joint_stiffness_MNm_rad=kreq/1e6,assumptions='Equivalent locked module-chain reference. Effective EI is an analyst-selected homogenised input, not a measured unit property. One central rotational spring; linear, small displacement, zero vertical slip; other contacts homogenised; selected L/300 criterion. Module-only support is a separate qualification task.')
(R/'data/interface_results.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='base'},indent=2))
