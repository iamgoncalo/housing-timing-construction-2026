from pathlib import Path
import json,csv,math
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import reportlab
R=Path(__file__).resolve().parents[1];O=R/'figures/swarm_v2';D=R/'data'
for n,f in [('V','Vera.ttf'),('VB','VeraBd.ttf')]:pdfmetrics.registerFont(TTFont(n,str(Path(reportlab.__file__).parent/'fonts'/f)))
units=[]
def add(role,x,y,z,dx=.6,dy=.3,dz=.24,course=0,col=0):
 units.append(dict(id=f'M{len(units)+1:04}',role=role,x=round(x,5),y=round(y,5),z=round(z,5),dx=dx,dy=dy,dz=dz,course=course,col=col))
for j in range(18):
 for i in range(7):add('floor',i*.6,j*.3,0,col=i)
for k in range(10):
 for side in [0,3.9]:
  for j in range(9):add('wall',side,j*.6,.24+k*.24,dx=.3,dy=.6,course=k+1)
 for end in [0,5.1]:
  for i in range(6):
   x=.3+i*.6
   if end==0 and i in [2,3] and k<9:continue
   add('wall',x,end,.24+k*.24,course=k+1)
for j in range(18):
 for i in range(7):add('roof',i*.6,j*.3,2.64,col=i)
for rib,x in enumerate([.6,3.]):
 for k in range(10):
  for j in range(8):
   for side in range(2):add('temporary',x+side*.3,.3+j*.6,.24+k*.24,dx=.3,dy=.6,course=k+1,col=rib)
assert len(units)==854
assert {k:sum(u['role']==k for u in units) for k in ['floor','wall','roof','temporary']}==dict(floor=126,wall=282,roof=126,temporary=320)
stages=[]
labels=['STAGING','FLOOR MAT','WALL COURSES','WALL RING','TEMPORARY RIBS','ROOF APPROACH','LOCK + TRANSFER','RECOVER RIB A','RETURN TO SWARM']
notes=[['854 identified units in the mission','Representative staging group shown'],['126 floor modules connected','Ground bearing + mat shear are gates'],['Five wall courses: 140 units','Corner locks + floor ties carry stability'],['282 wall units; 1.20 m doorway','Ring, corner and lintel contacts qualify'],['320 modules become two support ribs','0.60 m wide; 2.40 m high; floor-tied'],['108 roof units; 18 closure units free','Ribs support movement + edge duty'],['126 roof units locked; 320 supporting','Roof carries its accepted span before release'],['160 support units return to reserve','Roof state retained; rib B remains'],['534 building units + 320 in reserve','M0535 returns with its original identity']]
def status(u,k):
 if u['role']=='floor':return 'installed' if k>=1 else 'free'
 if u['role']=='wall':return 'installed' if k>=3 or (k==2 and u['course']<=5) else 'free'
 if u['role']=='roof':return 'installed' if k>=6 or (k==5 and u['col']!=3) else 'free'
 if u['role']=='temporary':return 'temporary' if 4<=k<=6 or (k==7 and u['col']==1) else 'free'
for k in range(9):
 states={u['id']:status(u,k) for u in units};counts={s:sum(v==s for v in states.values()) for s in ['installed','temporary','free']};assert sum(counts.values())==854
 stages.append(dict(stage=k,title=labels[k],counts=counts,states=states))
assert stages[-1]['counts']==dict(installed=534,temporary=0,free=320)
assert stages[4]['states']['M0535']=='temporary' and stages[7]['states']['M0535']=='free'
# Geometry is generated once. Every state references the same identified bodies.
# The references specify target poses, not a solved dynamic trajectory.
(D/'complete_sequence_units.json').write_text(json.dumps(units,indent=2))
(D/'complete_sequence_states.json').write_text(json.dumps(stages,indent=2))
# Gravity and stiffness screening for the EXACT cell, separate from earlier 3.60 m bay.
g=9.81;m=15.;q=1.5;A=4.2*5.4;L=3.9;a=.15;w=q*.3+m/.6*g/1000;EI=.25e6
M=w*(L*L/8-a*a/2);delta=(5*w*1000*L**4/384-w*1000*a*a*L*L/16)/EI
limit=L/300;kr=M*1000*L/(4*(limit-delta));roof=126*m*g/1000+q*A
res=dict(units=854,floor_units=126,wall_units=282,roof_units=126,temporary_units=320,final_building_units=534,returned_units=320,footprint_m=[4.2,5.4],clear_room_m=[3.6,4.8,2.4],unit_dimensions_m=[.6,.3,.24],unit_mass_kg=m,roof_area_m2=A,roof_selected_action_kN_m2=q,roof_total_gravity_kN=roof,roof_strip_width_m=.3,roof_strip_span_m=L,roof_strip_overhang_each_m=a,roof_strip_w_kN_m=w,roof_strip_Mmid_kNm=M,roof_strip_end_reaction_kN=w*4.2/2,selected_strip_effective_EI_Nm2=EI,roof_strip_bending_deflection_mm=delta*1000,selected_strip_limit_mm=limit*1000,minimum_selected_central_k_MNm_rad=kr/1e6,one_rib_weight_kN=160*m*g/1000,one_rib_plan_area_m2=.6*4.8,one_rib_pressure_all_roof_kPa=(roof+160*m*g/1000)/(.6*4.8),one_rib_gravity_restoring_moment_kNm=160*m*g/1000*.3,one_rib_full_compression_eccentricity_limit_m=.6/6,two_module_cantilever_gravity_moment_Nm=m*g*(.6+1.2),interpretation='Prescribed whole-building geometry, conserved identity inventory and gravity/stiffness screening. Selected loading and equivalent rigidity. These are required support and test conditions, not measured construction stability or autonomous execution.')
(D/'complete_sequence_engineering.json').write_text(json.dumps(res,indent=2))
# Compact equal-scale axonometric engineering plates, with diagrammatic roof transparency.
INK='#213D42';TEAL='#427D79';GOLD='#B07D46';MUTED='#6A7A7C';PAPER='#F4F1EA'
def txt(c,x,y,s,size=21,b=False,col=INK):
 c.setFont('VB' if b else 'V',size);c.setFillColor(HexColor(col));c.drawString(x,y,s)
def poly(c,pts,col,alpha=1,stroke='#9B9F9A'):
 c.saveState();c.setFillAlpha(alpha);c.setStrokeAlpha(max(.55,alpha));c.setFillColor(HexColor(col));c.setStrokeColor(HexColor(stroke));c.setLineWidth(.45);p=c.beginPath();p.moveTo(*pts[0]);[p.lineTo(*v) for v in pts[1:]];p.close();c.drawPath(p,stroke=1,fill=int(alpha>0));c.restoreState()
def cube(c,u,ox,oy,scale=34,alpha=1):
 def P(x,y,z):return ox+(x-y)*scale,oy+(x+y)*scale*.43+z*scale
 x,y,z=[u[t] for t in ['x','y','z']];dx,dy,dz=[u[t] for t in ['dx','dy','dz']]
 top=[P(x,y,z+dz),P(x+dx,y,z+dz),P(x+dx,y+dy,z+dz),P(x,y+dy,z+dz)]
 front=[P(x,y,z),P(x+dx,y,z),P(x+dx,y,z+dz),P(x,y,z+dz)]
 side=[P(x,y,z),P(x,y+dy,z),P(x,y+dy,z+dz),P(x,y,z+dz)]
 colors=('#E4D9C4','#C9BEA9','#F1EADD')
 if u['role']=='temporary':colors=('#6F9B94','#4C7C75','#A8C3BB')
 if u['id']=='M0535':colors=('#C99656','#A37239','#E8C790')
 for face,col in zip([front,side,top],colors):poly(c,face,col,alpha)
 # The same small contact mark is visible on every face family.
 px,py=P(x+dx*.5,y,z+dz*.55);c.saveState();c.setFillAlpha(alpha);c.setFillColor(HexColor(TEAL));c.circle(px,py,.8,stroke=0,fill=1);c.restoreState()
def reserve(c,x,y):
 for i in range(4):cube(c,dict(id='M0535' if i==0 else 'reserve',role='free',x=i*.6,y=0,z=0,dx=.6,dy=.3,dz=.24),x,y,22)
 txt(c,x-14,y-25,'Reserve outside the work view',17,col=MUTED)
for part in range(3):
 c=canvas.Canvas(str(O/f'construction_phase{part+1}.pdf'),pagesize=(1260,750),initialFontName='V')
 txt(c,40,700,['Material to supported walls','Support, climbing and roof closure','Load transfer and support recovery'][part],31,True)
 txt(c,40,658,'One 854-unit population | equal-scale views | teal: temporary duty | amber: M0535',22,col=MUTED)
 for j,k in enumerate(range(part*3,part*3+3)):
  left=25+j*420;ox=left+215;oy=280
  txt(c,left+15,590,f'S{k}  {labels[k]}',23,True)
  if k==0:
   # A representative part of the staging inventory, explicitly labelled, not a count proxy.
   for row in range(6):
    for col in range(5):cube(c,dict(id='M0535' if row==0 and col==0 else 'sample',role='free',x=col*.6,y=row*.3,z=0,dx=.6,dy=.3,dz=.24),ox-60,oy+35)
  else:
   shown=[u for u in units if status(u,k)!='free'];shown.sort(key=lambda u:(u['x']+u['y'],u['z']),reverse=True)
   for u in shown:cube(c,u,ox,oy,alpha=0 if (u['role']=='roof' and k>=5) or (u['role']=='wall' and u['y']==0 and k>=4) else 1)
  def P(x,y,z):return ox+(x-y)*34,oy+(x+y)*34*.43+z*34
  def arr(points,col):
   c.saveState();c.setStrokeColor(HexColor(col));c.setFillColor(HexColor(col));c.setLineWidth(1.6);c.setDash(5,3)
   for aa,bb in zip(points,points[1:]):c.line(*aa,*bb)
   aa,bb=points[-2:];ang=math.atan2(bb[1]-aa[1],bb[0]-aa[0]);p=c.beginPath();p.moveTo(*bb);p.lineTo(bb[0]-9*math.cos(ang-.4),bb[1]-9*math.sin(ang-.4));p.lineTo(bb[0]-9*math.cos(ang+.4),bb[1]-9*math.sin(ang+.4));p.close();c.setDash();c.drawPath(p,fill=1,stroke=0);c.restoreState()
  if k in [1,2]:
   arr([P(2.,-.6,.24),P(2.,.3,.24),P(.3,.3,.24 if k==1 else 1.44)],GOLD)
   txt(c,left+24,540,'Proposed approach / climb',18,col=GOLD)
  if k in [4,5]:
   arr([P(2.,.3,.24),P(1.2,.3,.24),P(1.2,.3,2.64),P(2.1,.15,2.88)],GOLD)
   txt(c,left+24,540,'Proposed rib-to-roof route',18,col=GOLD)
  if k in [6,7,8]:
   arr([P(4.05,1.,2.64),P(4.05,1.,.24),P(4.05,1.,0)],TEAL)
   txt(c,left+24,540,'Accepted wall-to-ground path required',17,col=TEAL)
  yy=235
  for ss in notes[k]:
   words=ss.split();line=''
   for word in words:
    test=(line+' '+word).strip()
    if pdfmetrics.stringWidth(test,'V',20)>385:
     txt(c,left+15,yy,line,20);yy-=23;line=word
    else:line=test
   txt(c,left+15,yy,line,20);yy-=23
  counts=stages[k]['counts'];txt(c,left+15,135,f"Installed {counts['installed']}  |  Support {counts['temporary']}",20,True);txt(c,left+15,101,f"Available {counts['free']}  |  Total 854",20)
  if status(next(u for u in units if u['id']=='M0535'),k)=='free':reserve(c,left+60,65)
  else:txt(c,left+15,45,'M0535 committed to rib A',19,col=GOLD)
 txt(c,40,15,'Prescribed geometric states and support requirements; front wall / roof outlined to expose internal support.',18,col=MUTED)
 c.showPage();c.save()
# A tabulated exact identity ledger in the article.
with (R/'tables/construction_inventory.tex').open('w') as f:
 f.write(r'''\begin{table}[!htbp]\centering\small
\caption{Conserved module identities through the selected whole-building construction sequence.}\label{tab:constructioninventory}
\begin{tabular}{@{}lrrrrr@{}}\toprule
State & Installed & Temporary & Available & Total & Self-weight (kN)\\\midrule
''')
 for s in stages:f.write(f"S{s['stage']}: {s['title'].lower()} & {s['counts']['installed']} & {s['counts']['temporary']} & {s['counts']['free']} & 854 & {(s['counts']['installed']+s['counts']['temporary'])*15*9.81/1000:.2f}"+r'\\'+'\n')
 f.write(r'''\bottomrule\end{tabular}
\end{table}
''')
print(json.dumps(res,indent=2))
