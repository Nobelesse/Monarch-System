/**
 * Offline, dependency-free illustrated 3D exercise simulator.
 * Geometry is projected from actual x/y/z positions with an orbiting camera.
 * It is a teaching visualization, NOT motion-capture or validated biomechanics.
 * Never label this as photorealistic, measured 4K footage, or exact technique.
 */
import type {OfflineExercise} from './offline-exercises';

type P = {x:number;y:number;z:number};
type Joints = Record<string,P>;
const p=(x:number,y:number,z:number):P=>({x,y,z});
const lerp=(a:number,b:number,t:number)=>a+(b-a)*t;
const mix=(a:P,b:P,t:number)=>p(lerp(a.x,b.x,t),lerp(a.y,b.y,t),lerp(a.z,b.z,t));
function poseCopy(j:Joints):Joints{return Object.fromEntries(Object.entries(j).map(([k,v])=>[k,{...v}]));}
function standard():Joints {
 const j:Joints={pelvis:p(0,1.01,0),chest:p(0,1.53,0),neck:p(0,1.79,0),head:p(0,1.94,0)};
 for(const side of [-1,1]){
  const k=side<0?'L':'R';j['shoulder'+k]=p(side*.275,1.68,0);j['elbow'+k]=p(side*.38,1.33,.03);j['hand'+k]=p(side*.40,1.02,.09);
  j['hip'+k]=p(side*.14,1,0);j['knee'+k]=p(side*.16,.56,.075);j['foot'+k]=p(side*.18,.105,.15);
 }
 return j;
}
function sit(j:Joints,amount=1){
 j.pelvis=p(0,1.01-.22*amount,-.09*amount);j.chest=p(0,1.53-.17*amount,.05*amount);j.neck=p(0,1.79-.17*amount,.08*amount);j.head=p(0,1.94-.17*amount,.08*amount);
 for(const s of [-1,1]) {const k=s<0?'L':'R'; j['shoulder'+k]=p(s*.275,1.68-.17*amount,.04);j['elbow'+k]=p(s*.39,1.36-.17*amount,.13);j['hand'+k]=p(s*.39,1.08-.15*amount,.20);j['hip'+k]=p(s*.14,1-.22*amount,-.09*amount);j['knee'+k]=p(s*(.17+.11*amount),.56-.07*amount,.08+.31*amount);}
}
function seated(j:Joints){sit(j,1);for(const s of [-1,1]){const k=s<0?'L':'R';j['knee'+k]=p(s*.20,.56,.43);j['foot'+k]=p(s*.20,.11,.45);}}
function supine(j:Joints){j.pelvis=p(0,.20,-.20);j.chest=p(0,.20,.23);j.neck=p(0,.20,.46);j.head=p(0,.22,.60);for(const s of [-1,1]){const k=s<0?'L':'R';j['hip'+k]=p(s*.16,.20,-.20);j['knee'+k]=p(s*.20,.54,-.57);j['foot'+k]=p(s*.20,.10,-.82);j['shoulder'+k]=p(s*.28,.20,.29);j['elbow'+k]=p(s*.40,.42,.32);j['hand'+k]=p(s*.45,.63,.35);}}
function plank(j:Joints,low=.28){j.pelvis=p(0,low,-.30);j.chest=p(0,low+.07,.24);j.neck=p(0,low+.08,.49);j.head=p(0,low+.08,.66);for(const s of [-1,1]){const k=s<0?'L':'R';j['hip'+k]=p(s*.14,low,-.3);j['knee'+k]=p(s*.17,low-.05,-.71);j['foot'+k]=p(s*.20,.10,-.98);j['shoulder'+k]=p(s*.26,low+.06,.25);j['elbow'+k]=p(s*.28,.20,.38);j['hand'+k]=p(s*.27,.10,.52);}}
function crouchHands(j:Joints){j.pelvis=p(0,.70,-.23);j.chest=p(0,.64,.12);j.neck=p(0,.64,.33);j.head=p(0,.68,.48);for(const s of [-1,1]){const k=s<0?'L':'R';j['hip'+k]=p(s*.15,.70,-.23);j['knee'+k]=p(s*.19,.10,-.58);j['foot'+k]=p(s*.19,.10,-.83);j['shoulder'+k]=p(s*.29,.64,.14);j['elbow'+k]=p(s*.32,.36,.30);j['hand'+k]=p(s*.32,.10,.44);}}
export function exerciseJoints(entry:OfflineExercise,phase:number):Joints {
 const a=(1-Math.cos(phase*2*Math.PI))/2;
 const j=standard();const mode=entry.pose;
 if(['sit_stand','squat','leg_press','lunge','step_up'].includes(mode)){
  if(mode==='sit_stand'||mode==='leg_press')sit(j,a*.95);
  else if(mode==='squat')sit(j,a);
  else if(mode==='lunge'){
   sit(j,.52*a);j['footL'].z+=.36;j['kneeL'].z+=.28;j['footR'].z-=.35;j['kneeR'].z-=.34;j['kneeR'].y-=.22*a;
  } else {sit(j,.20*a);j['kneeL'].y+=.22*a;j['footL'].y+=.32*a;j['footL'].z+=.31;}
  if(mode==='squat'||mode==='sit_stand')for(const k of ['L','R']){j['elbow'+k]=p(j['shoulder'+k].x*1.1,1.41-.12*a,.22);j['hand'+k]=p(j['shoulder'+k].x*1.15,1.30-.1*a,.44);}
 }
 else if(['hinge','single_hinge','back_extension'].includes(mode)){
  const drop=.32*a;j.pelvis.z-=.19*a;j.chest=p(0,1.53-drop,.36*a);j.neck=p(0,1.79-drop,.45*a);j.head=p(0,1.94-drop,.49*a);
  for(const s of [-1,1]){const k=s<0?'L':'R';j['shoulder'+k]=p(s*.27,1.68-drop,.37*a);j['elbow'+k]=p(s*.37,1.33-.33*a,.45*a);j['hand'+k]=p(s*.39,1.02-.43*a,.46*a);j['knee'+k].y-=.055*a;}
  if(mode==='single_hinge'){j['kneeR'].y+=.12*a;j['footR'].y+=.28*a;j['footR'].z-=.48*a;}
 }
 else if(mode==='bridge'){supine(j);j.pelvis.y+=.29*a;for(const s of [-1,1])j['hip'+(s<0?'L':'R')].y+=.29*a;}
 else if(['incline_push','floor_push'].includes(mode)){
  plank(j,mode==='floor_push'?.29:.56);
  if(mode==='incline_push'){
   j.pelvis.y=.84;j.chest.y=.92-.08*a;j.neck.y=.97-.08*a;j.head.y=1.00-.08*a;
   for(const s of [-1,1]){const k=s<0?'L':'R';j['hip'+k].y=.82;j['knee'+k].y=.50;j['shoulder'+k].y=.89-.08*a;j['elbow'+k]=p(s*.30,.82-.13*a,.54);j['hand'+k]=p(s*.31,.77,.73);}
  }else {j.chest.y-=.13*a;j.neck.y-=.13*a;j.head.y-=.13*a;for(const s of [-1,1]){const k=s<0?'L':'R';j['shoulder'+k].y-=.13*a;j['elbow'+k].y-=.11*a;}}
 }
 else if(['bench_press','seated_press','overhead_press','pec_fly'].includes(mode)){
  if(mode==='bench_press')supine(j);
  if(mode==='seated_press'||mode==='overhead_press'||mode==='pec_fly')seated(j);
  for(const s of [-1,1]){const k=s<0?'L':'R';const q=j['shoulder'+k];
   if(mode==='overhead_press'){j['elbow'+k]=p(s*.40,1.46+.25*a,.15);j['hand'+k]=p(s*.41,1.58+.55*a,.18);}
   else if(mode==='pec_fly'){j['elbow'+k]=p(s*(.57-.32*a),q.y-.10,.32);j['hand'+k]=p(s*(.76-.61*a),q.y-.14,.50);}
   else if(mode==='bench_press'){j['elbow'+k]=p(s*.38,.38+.28*a,.25);j['hand'+k]=p(s*.40,.45+.39*a,.29);}
   else {j['elbow'+k]=p(s*.37,q.y-.22,.28+.14*a);j['hand'+k]=p(s*.38,q.y-.25,.25+.53*a);}
  }
 }
 else if(['scapular','prone_raise','row','band_apart','towel_hold','lat_pulldown'].includes(mode)){
  if(mode==='prone_raise'){plank(j,.20);for(const s of [-1,1]){const k=s<0?'L':'R';j['elbow'+k]=p(s*.54,.25+.13*a,.28);j['hand'+k]=p(s*.67,.36+.15*a,.33);}}
  else if(mode==='lat_pulldown'){
   seated(j);for(const s of [-1,1]){const k=s<0?'L':'R';j['elbow'+k]=p(s*.54,1.73-.30*a,.07);j['hand'+k]=p(s*.62,2.22-.54*a,.05);}
  }else if(mode==='band_apart'||mode==='towel_hold'){
   for(const s of [-1,1]){const k=s<0?'L':'R';const base=mode==='towel_hold'?.48:.23;const stretch=mode==='towel_hold'?.08:.49;const dist=base+stretch*a;j['elbow'+k]=p(s*(dist*.81),1.40,.25);j['hand'+k]=p(s*dist,1.46,.42);}
  }else if(mode==='row'){
   if(entry.slug.includes('seated')||entry.slug.includes('chest-supported'))seated(j);
   else if(entry.slug.includes('dumbbell')||entry.slug.includes('kettlebell')){
    j.chest.z+=.30;j.head.z+=.32;for(const s of [-1,1])j['shoulder'+(s<0?'L':'R')].z+=.29;
   }
   for(const s of [-1,1]){const k=s<0?'L':'R';j['elbow'+k]=p(s*.42,1.32,.13-.32*a);j['hand'+k]=p(s*.45,1.20,.57-.49*a);}
  }else for(const s of [-1,1]){const k=s<0?'L':'R';j['elbow'+k]=p(s*(.28+.13*a),1.45,.06);j['hand'+k]=p(s*(.3+.18*a),1.28,.05);}
 }
 else if(['brace','pallof','carry','knee_lift','seated_march','dead_bug','bird_dog','side_plank'].includes(mode)){
  if(mode==='dead_bug'){
   supine(j);j['handL'].z+=.25*a;j['kneeR'].y-=.27*a;j['footR'].z-=.25*a;
  }else if(mode==='bird_dog'){
   crouchHands(j);j['handL'].z+=.51*a;j['handL'].y+=.17*a;j['footR'].z-=.55*a;j['footR'].y+=.26*a;j['kneeR'].y+=.08*a;
  }else if(mode==='side_plank'){
   plank(j,.25+.15*a);j['shoulderR'].y+=.28;j['elbowR'].y+=.42;j['handR'].y+=.70;j['kneeL'].y=.1;
  }else if(mode==='seated_march'){
   seated(j);j['kneeL'].y+=.23*a;j['footL'].y+=.18*a;
  }else if(mode==='knee_lift'){
   j['kneeL'].y+=.46*a;j['kneeL'].z+=.24*a;j['footL'].y+=.30*a;
  }else if(mode==='pallof')for(const s of [-1,1]){const k=s<0?'L':'R';j['elbow'+k]=p(s*.20,1.42,.28+.28*a);j['hand'+k]=p(s*.13,1.39,.34+.48*a);}
  else if(mode==='carry')for(const s of [-1,1]){const k=s<0?'L':'R';j['hand'+k].y=.97+.04*a;j['foot'+k].z+=s*.04*a;}
  else {j.chest.y+=.01*a;j.head.y+=.01*a;}
 }
 else if(['calf_raise','calf_stretch','shoulder_circles','side_reach','torso_rotation','ankle_circles','neck_turns','wrist_circles','hip_circles','band_mobility'].includes(mode)){
  if(mode==='calf_raise'){j.pelvis.y+=.09*a;j.chest.y+=.09*a;j.head.y+=.09*a;for(const s of [-1,1])j['foot'+(s<0?'L':'R')].y+=.045*a;}
  else if(mode==='calf_stretch'){j['footL'].z-=.46;j['kneeL'].z-=.15*a;j.chest.z+=.13+.04*a;for(const s of [-1,1]){const k=s<0?'L':'R';j['hand'+k]=p(s*.34,1.44,.52);j['elbow'+k]=p(s*.35,1.38,.31);}}
  else if(mode==='shoulder_circles'){seated(j);for(const s of [-1,1]){const k=s<0?'L':'R';j['elbow'+k].x+=s*.10*a;j['elbow'+k].y+=.11*a;}}
  else if(mode==='side_reach'){j['handL']=p(-.43,1.86+.19*a,.05);j['elbowL']=p(-.35,1.84,.02);j.head.x+=.08*a;j.chest.x+=.09*a;}
  else if(mode==='torso_rotation'){seated(j);for(const s of [-1,1]){const k=s<0?'L':'R';j['shoulder'+k].z+=s*.20*a;j['elbow'+k].z+=s*.12*a;j['hand'+k].z+=s*.10*a;}}
  else if(mode==='ankle_circles'){seated(j);j['footL'].x+=.10*Math.sin(2*Math.PI*phase);j['footL'].y+=.10*Math.cos(2*Math.PI*phase);}
  else if(mode==='neck_turns'){j.head.x+=.065*Math.sin(2*Math.PI*phase);}
  else if(mode==='wrist_circles'){j['handL'].x+=.09*Math.cos(phase*2*Math.PI);j['handL'].y+=.09*Math.sin(phase*2*Math.PI);}
  else if(mode==='hip_circles'){j.pelvis.x+=.08*Math.sin(phase*2*Math.PI);j.pelvis.z+=.08*Math.cos(phase*2*Math.PI);}
  else if(mode==='band_mobility')for(const s of [-1,1]){const k=s<0?'L':'R';j['hand'+k].y=1.48+.46*a;j['elbow'+k].y=1.45+.30*a;}
 }
 return j;
}

type Camera = {w:number;h:number;yaw:number;project:(v:P)=>{x:number;y:number;d:number;scale:number}};
function makeCamera(w:number,h:number,deg:number):Camera{
 const yaw=deg*Math.PI/180;
 return {w,h,yaw,project(v:P){const x=v.x*Math.cos(yaw)-v.z*Math.sin(yaw);const d=v.x*Math.sin(yaw)+v.z*Math.cos(yaw);const zoom=1/(1+Math.max(-1.1,d)*.15);const scale=Math.min(w/3.9,h/2.55)*zoom;return {x:w*.52+x*scale,y:h*.90-v.y*scale+d*8,d,scale};}};
}
const grad=(ctx:CanvasRenderingContext2D,x1:number,y1:number,x2:number,y2:number,stops:string[])=>{const g=ctx.createLinearGradient(x1,y1,x2,y2);g.addColorStop(0,stops[0]);g.addColorStop(.28,stops[1]);g.addColorStop(.69,stops[2]);g.addColorStop(1,stops[3]);return g;};
function capsule(ctx:CanvasRenderingContext2D,c:Camera,a:P,b:P,r:number,tones:string[]){
 const u=c.project(a),v=c.project(b);const width=r*(u.scale+v.scale);
 ctx.lineCap='round';ctx.lineJoin='round';ctx.lineWidth=width;
 ctx.strokeStyle=grad(ctx,Math.min(u.x,v.x)-width,0,Math.max(u.x,v.x)+width,0,tones);
 ctx.beginPath();ctx.moveTo(u.x,u.y);ctx.lineTo(v.x,v.y);ctx.stroke();
 ctx.strokeStyle='rgba(255,255,255,0.11)';ctx.lineWidth=Math.max(.6,width*.24);ctx.beginPath();ctx.moveTo(u.x-width*.13,u.y);ctx.lineTo(v.x-width*.13,v.y);ctx.stroke();
}
function oval(ctx:CanvasRenderingContext2D,c:Camera,v:P,rx:number,ry:number,tones:string[]){const t=c.project(v),r=Math.max(1,rx*t.scale);ctx.beginPath();ctx.ellipse(t.x,t.y,r,Math.max(1,ry*t.scale),0,0,2*Math.PI);ctx.fillStyle=grad(ctx,t.x-r,t.y,t.x+r,t.y,tones);ctx.fill();ctx.strokeStyle='rgba(255,240,234,.17)';ctx.lineWidth=1;ctx.stroke();}
function roundBox(ctx:CanvasRenderingContext2D,c:Camera,v:P,w:number,h:number,color:string){const o=c.project(v);ctx.fillStyle=color;ctx.fillRect(o.x-w*o.scale/2,o.y-h*o.scale/2,w*o.scale,h*o.scale);}

function panel(ctx:CanvasRenderingContext2D,c:Camera,center:P,width:number,height:number,color:string,stroke='rgba(171,144,230,.14)'){
 const o=c.project(center);const w=width*o.scale,h=height*o.scale;ctx.fillStyle=color;ctx.fillRect(o.x-w/2,o.y-h/2,w,h);ctx.strokeStyle=stroke;ctx.lineWidth=1;ctx.strokeRect(o.x-w/2,o.y-h/2,w,h);
}
function drawArrow(ctx:CanvasRenderingContext2D,ax:number,ay:number,bx:number,by:number,color:string){
 ctx.strokeStyle=color;ctx.fillStyle=color;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(ax,ay);ctx.lineTo(bx,by);ctx.stroke();
 const ang=Math.atan2(by-ay,bx-ax),len=10;ctx.beginPath();ctx.moveTo(bx,by);ctx.lineTo(bx-len*Math.cos(ang-.45),by-len*Math.sin(ang-.45));ctx.lineTo(bx-len*Math.cos(ang+.45),by-len*Math.sin(ang+.45));ctx.closePath();ctx.fill();
}
function tracedJoints(entry:OfflineExercise){
 switch(entry.pose){
  case 'incline_push': return ['shoulderL','shoulderR','head'];
  case 'floor_push': return ['chest','head'];
  case 'sit_stand': case 'squat': return ['pelvis','kneeL','kneeR'];
  case 'lunge': case 'step_up': return ['kneeL','footL','pelvis'];
  case 'hinge': case 'single_hinge': case 'back_extension': return ['chest','head','pelvis'];
  case 'bridge': return ['pelvis'];
  case 'row': case 'band_apart': case 'towel_hold': case 'lat_pulldown': return ['handL','handR','elbowL','elbowR'];
  case 'dead_bug': case 'bird_dog': return ['handL','footR'];
  case 'seated_march': case 'knee_lift': return ['kneeL','footL'];
  case 'calf_raise': return ['head','pelvis'];
  case 'calf_stretch': return ['chest'];
  case 'side_reach': return ['handL'];
  case 'torso_rotation': return ['shoulderL','shoulderR'];
  case 'ankle_circles': return ['footL'];
  case 'wrist_circles': return ['handL'];
  case 'hip_circles': return ['pelvis'];
  default: return [];
 }
}
function scene(ctx:CanvasRenderingContext2D,c:Camera,e:OfflineExercise){
 const {w,h}=c;const back=ctx.createLinearGradient(0,0,w,h);back.addColorStop(0,'#101325');back.addColorStop(.5,'#19142b');back.addColorStop(1,'#070b17');ctx.fillStyle=back;ctx.fillRect(0,0,w,h);
 const halo=ctx.createRadialGradient(w*.52,h*.46,8,w*.52,h*.46,w*.54);halo.addColorStop(0,'rgba(144,96,249,.25)');halo.addColorStop(1,'rgba(144,96,249,0)');ctx.fillStyle=halo;ctx.fillRect(0,0,w,h);
 const floor=c.project(p(0,0,0));ctx.strokeStyle='rgba(184,150,245,.15)';ctx.lineWidth=1;
 for(let i=-4;i<=4;i++){const a=c.project(p(i*.28,.02,-1.2)),b=c.project(p(i*.28,.02,1.4));ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}
 for(let i=-3;i<=4;i++){const a=c.project(p(-1.3,.02,i*.30)),b=c.project(p(1.3,.02,i*.30));ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}
 const s=e.support;
 if(s==='wall'){
  panel(ctx,c,p(0,1.08,.96),2.25,1.95,'rgba(74,70,112,.38)','rgba(200,185,255,.15)');
  const stripe=c.project(p(0,1.18,.95));ctx.fillStyle='rgba(193,176,246,.11)';ctx.fillRect(stripe.x-150,stripe.y-2,300,4);
 }
 if(s==='counter'){
  panel(ctx,c,p(0,.47,.98),2.05,.82,'rgba(95,102,126,.30)','rgba(180,190,230,.12)');
  const lip=c.project(p(0,.82,.88));ctx.fillStyle='#7d859c';ctx.fillRect(lip.x-155,lip.y-7,310,14);
 }
 if(['bench','chair'].includes(s)||['seated_march','sit_stand','shoulder_circles','torso_rotation','ankle_circles','seated_march'].includes(e.pose)){
  roundBox(ctx,c,p(0,.63,-.22),.80,.09,'#323c53');for(const x of [-.30,.30])capsule(ctx,c,p(x,.58,-.30),p(x,.05,-.30),.027,['#111724','#536078','#283448','#10131d']);
  if(s==='bench') panel(ctx,c,p(0,.86,-.30),.88,.12,'rgba(65,72,98,.42)');
 }
 if(s==='step'){
  roundBox(ctx,c,p(-.18,.17,.48),.70,.30,'#454052');
  panel(ctx,c,p(-.18,.33,.48),.72,.04,'rgba(164,167,189,.12)');
 }
 if(s==='machine'||e.pose==='lat_pulldown'){
  for(const x of [-.67,.67])capsule(ctx,c,p(x,.08,.48),p(x,2.16,.48),.022,['#151823','#6d7792','#353b58','#16192a']);
  capsule(ctx,c,p(-.67,2.16,.48),p(.67,2.16,.48),.02,['#151823','#6d7792','#353b58','#16192a']);
  if(e.pose==='lat_pulldown')capsule(ctx,c,p(-.28,1.95,.10),p(.28,1.95,.10),.022,['#d1d7ef','#5b6483','#bcc3de','#3f4763']);
 }
 if((s==='bench'||e.pose==='incline_push') && s!=='wall' && s!=='counter'){
  roundBox(ctx,c,p(0,.82,.70),1.06,.10,'#5a6178'); for(const x of [-.42,.42])capsule(ctx,c,p(x,.76,.70),p(x,.10,.70),.03,['#23253d','#74768b','#39374a','#151629']);
 }
 // grounded shadow
 ctx.fillStyle='rgba(0,0,0,.32)';ctx.beginPath();ctx.ellipse(floor.x,floor.y,94,17,0,0,Math.PI*2);ctx.fill();
}
export function paintHuman(ctx:CanvasRenderingContext2D,w:number,h:number,entry:OfflineExercise,phase:number,cameraDegrees:number){
 const c=makeCamera(w,h,cameraDegrees);scene(ctx,c,entry);const j=exerciseJoints(entry,phase);
 const startPose=exerciseJoints(entry,0.08),endPose=exerciseJoints(entry,0.58);
 const skin=['#6d5148','#ddb19b','#b98073','#574241'];const shirt=['#081224','#47536f','#1a233d','#090f1f'];const short=['#111a2b','#49506a','#1b2132','#0a0d1c'];
 const shoe=['#090c17','#72738e','#30334b','#080911'];
 const things:{depth:number;draw:()=>void}[]=[];
 function limb(a:string,b:string,r:number,tones:string[]){if(!j[a]||!j[b])return;things.push({depth:(c.project(j[a]).d+c.project(j[b]).d)/2,draw:()=>capsule(ctx,c,j[a],j[b],r,tones)});}
 function drawGhost(jg:Joints,alpha:number){
  ctx.save();ctx.globalAlpha=alpha;
  for(const k of ['L','R']){capsule(ctx,c,jg['hip'+k],jg['knee'+k],.065,['#5c5d88','#a59de6','#746fb7','#4d527b']);capsule(ctx,c,jg['knee'+k],jg['foot'+k],.055,['#5c5d88','#a59de6','#746fb7','#4d527b']);capsule(ctx,c,jg['shoulder'+k],jg['elbow'+k],.05,['#5c5d88','#a59de6','#746fb7','#4d527b']);capsule(ctx,c,jg['elbow'+k],jg['hand'+k],.04,['#5c5d88','#a59de6','#746fb7','#4d527b']);}
  capsule(ctx,c,jg.pelvis,jg.chest,.13,['#5c5d88','#a59de6','#746fb7','#4d527b']);oval(ctx,c,jg.head,.09,.12,['#5c5d88','#a59de6','#746fb7','#4d527b']);
  ctx.restore();
 }
 // draw start/end motion reference ghosts first for easier beginner understanding
 drawGhost(startPose,.18); drawGhost(endPose,.12);
 // main figure
 for(const k of ['L','R']){
  const thighEnd=mix(j['hip'+k],j['knee'+k],.42);
  things.push({depth:c.project(j['hip'+k]).d,draw:()=>capsule(ctx,c,j['hip'+k],thighEnd,.115,short)});
  things.push({depth:c.project(j['knee'+k]).d,draw:()=>capsule(ctx,c,thighEnd,j['knee'+k],.076,skin)});
  limb('knee'+k,'foot'+k,.066,skin);
  things.push({depth:c.project(j['foot'+k]).d,draw:()=>oval(ctx,c,p(j['foot'+k].x,j['foot'+k].y,j['foot'+k].z+.045),.12,.06,shoe)});
  limb('shoulder'+k,'elbow'+k,.075,skin);limb('elbow'+k,'hand'+k,.055,skin);
  things.push({depth:c.project(j['hand'+k]).d,draw:()=>oval(ctx,c,j['hand'+k],.053,.068,skin)});
 }
 things.push({depth:c.project(j.pelvis).d,draw:()=>oval(ctx,c,j.pelvis,.24,.19,short)});
 things.push({depth:c.project(j.chest).d,draw:()=>{capsule(ctx,c,j.pelvis,j.chest,.205,shirt);oval(ctx,c,j.chest,.27,.21,shirt);}});
 things.push({depth:c.project(j.neck).d,draw:()=>capsule(ctx,c,j.neck,j.head,.067,skin)});
 things.push({depth:c.project(j.head).d,draw:()=>{
  oval(ctx,c,j.head,.112,.149,skin);
  const hp=c.project(j.head);const zz=hp.scale;
  ctx.fillStyle='#161524';ctx.beginPath();ctx.ellipse(hp.x,hp.y-.10*zz,.107*zz,.063*zz,-.10,Math.PI,2*Math.PI);ctx.fill();
  ctx.fillStyle='#27202a';for(const n of [-1,1]){ctx.beginPath();ctx.ellipse(hp.x+n*.035*zz,hp.y-.01*zz,Math.max(.7,.009*zz),Math.max(.7,.007*zz),0,0,2*Math.PI);ctx.fill();}
  ctx.strokeStyle='rgba(92,46,44,.7)';ctx.lineWidth=Math.max(.5,.005*zz);ctx.beginPath();ctx.moveTo(hp.x,hp.y+.01*zz);ctx.lineTo(hp.x-.006*zz,hp.y+.035*zz);ctx.stroke();ctx.beginPath();ctx.moveTo(hp.x-.023*zz,hp.y+.066*zz);ctx.lineTo(hp.x+.026*zz,hp.y+.066*zz);ctx.stroke();
 }});
 things.sort((a,b)=>b.depth-a.depth);for(const o of things)o.draw();
 // equipment overlays
 if(entry.pose==='towel_hold'||entry.pose==='band_apart'||entry.support==='resistance_bands'){
  const h1=c.project(j.handL),h2=c.project(j.handR);ctx.strokeStyle=entry.pose==='towel_hold'?'#d9dbe8':'#3eb9b1';ctx.lineWidth=entry.pose==='towel_hold'?6:3;ctx.beginPath();ctx.moveTo(h1.x,h1.y);ctx.lineTo(h2.x,h2.y);ctx.stroke();
 }
 if(entry.support==='dumbbells'||entry.support==='kettlebell')for(const k of ['L','R']){
  const v=j['hand'+k];if(!v)continue;const o=c.project(v);ctx.fillStyle='#737c93';ctx.fillRect(o.x-19,o.y-5,38,10);ctx.fillStyle='#232c3e';ctx.fillRect(o.x-22,o.y-12,9,25);ctx.fillRect(o.x+13,o.y-12,9,25);
 }
 // movement arrows on the most important joints
 ctx.save(); ctx.globalAlpha=.75; const keys=tracedJoints(entry);
 for(const key of keys){ if(!(key in startPose) || !(key in endPose)) continue; const a=c.project((startPose as any)[key]), b=c.project((endPose as any)[key]); if(Math.hypot(b.x-a.x,b.y-a.y)<16) continue; drawArrow(ctx,a.x,a.y,b.x,b.y,'rgba(193,165,255,.72)'); }
 ctx.restore();
 ctx.fillStyle='rgba(231,222,255,.85)';ctx.font=`${Math.max(11,Math.round(w/72))}px system-ui, sans-serif`;ctx.fillText('OFFLINE GUIDED HUMAN DEMO • ENVIRONMENT-AWARE',20,h-18);
}
