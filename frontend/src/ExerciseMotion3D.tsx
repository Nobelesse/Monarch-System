/** Procedural 3D joint model for beginner ORIENTATION, not an exercise-specific motion capture. */
import {useEffect, useRef, useState} from 'react';
import './exercise-motion.css';

type Movement = 'squat'|'hinge'|'push'|'pull'|'core'|'mobility';
type V3 = [number,number,number];
type Bone = [string,string];
const links: Bone[] = [
 ['hipL','hipR'],['hipL','kneeL'],['kneeL','ankleL'],['hipR','kneeR'],['kneeR','ankleR'],
 ['hipL','shoulderL'],['hipR','shoulderR'],['shoulderL','shoulderR'],
 ['shoulderL','elbowL'],['elbowL','wristL'],['shoulderR','elbowR'],['elbowR','wristR'],['neck','head'],
];
const movementNotes:Record<Movement,{name:string;cue:string;common:string}>= {
 squat:{name:'Squat pattern',cue:'Bend at hips and knees while keeping the movement comfortable.',common:'Keep feet planted; avoid collapsing the knees inward.'},
 hinge:{name:'Hip hinge pattern',cue:'Send hips backward and return to a tall posture with control.',common:'Keep movement from the hips; avoid rounding your back deliberately.'},
 push:{name:'Push pattern',cue:'Press away steadily and return without rushing.',common:'Keep shoulders comfortable; do not force painful overhead ranges.'},
 pull:{name:'Pull pattern',cue:'Draw elbows toward the ribs or behind the body, then extend with control.',common:'Avoid shrugging forcefully or throwing the weight.'},
 core:{name:'Core bracing pattern',cue:'Brace gently and move slowly while maintaining a comfortable spine.',common:'Breathe normally; avoid holding your breath for long periods.'},
 mobility:{name:'Mobility pattern',cue:'Reach through a gentle comfortable range and return slowly.',common:'Do not force a stretch or push through pain.'},
};
const mix=(a:number,b:number,f:number)=>a+(b-a)*f;
function point(x:number,y:number,z:number):V3{return [x,y,z];}
function skeleton(movement:Movement, phase:number):Record<string,V3>{
 // All positions are actual XYZ joint coordinates in a small 3D scene.
 const f=(1-Math.cos(phase*2*Math.PI))/2;
 const bend=movement==='squat'?f*.63:movement==='hinge'?f*.2:0;
 const hipY=1.35-bend;
 const torso=movement==='hinge'?f*.63:movement==='core'?Math.sin(phase*2*Math.PI)*.16:0;
 const shoulderY=hipY+1.03-(movement==='core'?Math.abs(torso)*.1:0);
 const shoulderZ=torso*.8;
 const kneeY=mix(.74,.62,bend);const kneeZ=movement==='squat'?f*.46:movement==='hinge'?f*.1:0;
 const hipZ=movement==='hinge'?-f*.34:0;
 const positions:Record<string,V3>={
 hipL:point(-.22,hipY,hipZ),hipR:point(.22,hipY,hipZ),
 kneeL:point(-.23,kneeY,kneeZ),kneeR:point(.23,kneeY,kneeZ),
 ankleL:point(-.25,.09,.12),ankleR:point(.25,.09,.12),
 shoulderL:point(-.38,shoulderY,shoulderZ),shoulderR:point(.38,shoulderY,shoulderZ),
 neck:point(0,shoulderY+.09,shoulderZ),head:point(0,shoulderY+.37,shoulderZ),
 elbowL:point(-.58,shoulderY-.43,shoulderZ+.06),elbowR:point(.58,shoulderY-.43,shoulderZ+.06),
 wristL:point(-.56,shoulderY-.87,shoulderZ+.18),wristR:point(.56,shoulderY-.87,shoulderZ+.18),
 };
 if(movement==='push'){
  for(const sign of [-1,1] as const){const label=sign<0?'L':'R';
   positions[`elbow${label}`]=point(sign*(.63-.11*f),shoulderY-.32+.31*f,shoulderZ+.26+.29*f);
   positions[`wrist${label}`]=point(sign*.48,shoulderY-.30+.49*f,shoulderZ+.45+.43*f);
  }
 }else if(movement==='pull'){
  for(const sign of [-1,1] as const){const label=sign<0?'L':'R';
   positions[`elbow${label}`]=point(sign*(.52+.21*f),shoulderY-.35,shoulderZ+.5-.52*f);
   positions[`wrist${label}`]=point(sign*.55,shoulderY-.31,shoulderZ+.86-.72*f);
  }
 }else if(movement==='mobility'){
  for(const sign of [-1,1] as const){const label=sign<0?'L':'R';
   positions[`elbow${label}`]=point(sign*(.61-.34*f),shoulderY-.38+.69*f,shoulderZ+.05);
   positions[`wrist${label}`]=point(sign*(.66-.38*f),shoulderY-.78+1.35*f,shoulderZ+.05);
  }
 }else if(movement==='core'){
  positions.head[0]=.22*Math.sin(phase*2*Math.PI);
  positions.neck[0]=positions.head[0]*.7;
 }
 return positions;
}
export default function ExerciseMotion3D({name,movement}:{name:string;movement:Movement}){
 const canvas=useRef<HTMLCanvasElement>(null);
 const [playing,setPlaying]=useState(true);
 const [view,setView]=useState(25);
 const [speed,setSpeed]=useState(1);
 const [motion,setMotion]=useState(false);
 const notes=movementNotes[movement];
 useEffect(()=>{
  let reduced=false;
  const mq=window.matchMedia('(prefers-reduced-motion: reduce)');
  reduced=mq.matches;setMotion(!reduced);if(reduced)setPlaying(false);
 },[]);
 useEffect(()=>{
  const element=canvas.current;if(!element)return;
  const context=element.getContext('2d');if(!context)return;
  let raf=0;let last=0;let elapsed=0;
  const render=(time:number)=>{
   if(last){const delta=Math.min((time-last)/1000,.05);if(playing&&motion)elapsed+=delta*speed;}
   last=time;
   const rect=element.getBoundingClientRect();const width=Math.max(260,rect.width);const height=Math.max(220,rect.height);
   const ratio=Math.min(2,window.devicePixelRatio||1);
   if(element.width!==Math.round(width*ratio)||element.height!==Math.round(height*ratio)){
    element.width=Math.round(width*ratio);element.height=Math.round(height*ratio);
   }
   context.setTransform(ratio,0,0,ratio,0,0);context.clearRect(0,0,width,height);
   const phase=(elapsed/2.8)%1;const yaw=view*Math.PI/180;const scale=Math.min(height/3.45,width/3.7);
   const project=(a:V3)=>{const [x,y,z]=a;const xx=x*Math.cos(yaw)+z*Math.sin(yaw);const zz=-x*Math.sin(yaw)+z*Math.cos(yaw);const p=3.9/(3.9+zz*.24);
    return {x:width*.5+xx*scale*p,y:height*.88-y*scale*p,z:zz};};
   context.strokeStyle='rgba(119,98,230,.17)';context.lineWidth=1;
   for(let i=-4;i<=4;i++){
    const a=project([i*.45,0,-1.7]),b=project([i*.45,0,1.7]);
    const c=project([-1.7,0,i*.45]),d=project([1.7,0,i*.45]);
    context.beginPath();context.moveTo(a.x,a.y);context.lineTo(b.x,b.y);context.stroke();
    context.beginPath();context.moveTo(c.x,c.y);context.lineTo(d.x,d.y);context.stroke();
   }
   const joints=skeleton(movement,phase);
   const joints2=Object.fromEntries(Object.entries(joints).map(([key,p])=>[key,project(p)]));
   const drawLinks=links.map(([a,b])=>({a,b,depth:(joints2[a].z+joints2[b].z)/2})).sort((a,b)=>b.depth-a.depth);
   for(const link of drawLinks){
    const a=joints2[link.a],b=joints2[link.b];const active=link.a.includes('shoulder')||link.a.includes('elbow')||link.a.includes('hip');
    context.lineCap='round';context.lineJoin='round';context.beginPath();context.moveTo(a.x,a.y);context.lineTo(b.x,b.y);
    context.strokeStyle='rgba(19,10,41,.98)';context.lineWidth=15;context.stroke();
    context.strokeStyle=active?'#b29bff':'#8295c5';context.lineWidth=9;context.stroke();
    context.strokeStyle=active?'rgba(239,223,255,.7)':'rgba(210,230,255,.52)';context.lineWidth=2;context.stroke();
   }
   const head=joints2.head;context.beginPath();context.arc(head.x,head.y,15,0,Math.PI*2);
   context.fillStyle='#998de7';context.fill();context.strokeStyle='#e5ccff';context.lineWidth=2;context.stroke();
   for(const [key,p] of Object.entries(joints2))if(key!=='head'&&key!=='neck'){
    context.beginPath();context.arc(p.x,p.y,4.7,0,Math.PI*2);
    context.fillStyle='#d4c3ff';context.fill();
   }
   context.fillStyle='rgba(201,188,255,.8)';context.font='10px system-ui';
   context.fillText('3D MOTION / ORIENTATION',14,19);
   context.textAlign='right';context.fillText(`${Math.round((phase*100))}%`,width-12,19);context.textAlign='left';
   raf=requestAnimationFrame(render);
  };
  raf=requestAnimationFrame(render);return()=>cancelAnimationFrame(raf);
 },[movement,view,playing,speed,motion]);
 return <section className="motion-wrap" aria-label={`3D motion preview for ${name}`}>
  <div className="motion-header"><span className="motion-label">◇ INTERACTIVE MOTION GUIDE</span><strong>{notes.name}</strong></div>
  <div className="motion-view"><canvas ref={canvas} role="img" aria-label={`Rotatable 3D skeletal demonstration of the ${notes.name.toLowerCase()} for ${name}`} /></div>
  <div className="motion-controls"><button type="button" onClick={()=>{setMotion(true);setPlaying(v=>!v);}}>{playing&&motion?'Ⅱ Pause':'▶ Play'}</button>
   <label>Rotate <input type="range" aria-label="Rotate 3D figure" min="-85" max="85" value={view} onChange={e=>setView(Number(e.target.value))}/></label>
   <label>Speed <select aria-label="Motion speed" value={speed} onChange={e=>setSpeed(Number(e.target.value))}><option value="0.5">0.5×</option><option value="1">1×</option><option value="1.5">1.5×</option></select></label>
  </div>
  <p className="motion-cue"><b>Movement cue:</b> {notes.cue}</p>
  <p className="motion-caution"><b>Beginner tip:</b> {notes.common}</p>
  <p className="motion-disclaimer">Illustrative 3D movement-family preview, not exact technique for every named exercise. Follow the exercise-specific written instructions and consult a qualified coach when unsure.</p>
 </section>;
}
