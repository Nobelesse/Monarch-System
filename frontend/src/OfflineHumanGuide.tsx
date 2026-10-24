import {useEffect,useRef,useState} from 'react';
import {OFFLINE_EXERCISES,OFFLINE_EXERCISE_COUNT, type OfflineExercise} from './offline-exercises';
import {paintHuman} from './offline-human-renderer';
import './offline-human-guide.css';

type Movement='squat'|'hinge'|'push'|'pull'|'core'|'mobility';
const tips:Record<Movement,string>={
 squat:'Keep your feet steady; bend through a comfortable range; control the return.',
 hinge:'Move from the hips, not by rounding your lower back. Keep the load close.',
 push:'Move slowly and maintain a steady line through your body. Avoid locking joints hard.',
 pull:'Keep your torso steady; pull smoothly rather than swinging.',
 core:'Breathe normally, avoid bracing so hard you hold your breath, and stay controlled.',
 mobility:'Use slow pain-free ranges, with no bouncing or forced stretching.'
};

function suggestedView(exercise?:OfflineExercise){
 if(!exercise)return 32;
 if(exercise.support==='wall')return 62;
 if(exercise.support==='counter'||exercise.support==='bench'||exercise.pose==='incline_push')return 58;
 if(['floor_push','bridge','bench_press','dead_bug','bird_dog','side_plank','calf_stretch'].includes(exercise.pose))return 54;
 if(['row','lat_pulldown','towel_hold','band_apart','pallof'].includes(exercise.pose))return 42;
 if(['squat','sit_stand','lunge','step_up','hinge','single_hinge'].includes(exercise.pose))return 26;
 return 32;
}

export default function OfflineHumanGuide({slug,name,movement,instructions}:{slug:string;name:string;movement:Movement;instructions:string}){
 const exercise=OFFLINE_EXERCISES[slug];
 const canvas=useRef<HTMLCanvasElement>(null);
 const time=useRef(0);
 const raf=useRef(0);
 const [playing,setPlaying]=useState(true);
 const [speed,setSpeed]=useState(.75);
 const [view,setView]=useState(()=>suggestedView(exercise));
 const [progress,setProgress]=useState(0);
 const [motionAllowed,setMotionAllowed]=useState(true);
 useEffect(()=>{
  const media=window.matchMedia('(prefers-reduced-motion: reduce)');
  const update=()=>setMotionAllowed(!media.matches);update();
  media.addEventListener?.('change',update);return()=>media.removeEventListener?.('change',update);
 },[]);
 useEffect(()=>{time.current=0;setProgress(0);setView(suggestedView(exercise));},[slug,exercise]);
 useEffect(()=>{
  if(!exercise)return;
  let prior=0;const render=(now:number)=>{
   const node=canvas.current;if(!node)return;
   const box=node.getBoundingClientRect();const dpr=Math.min(window.devicePixelRatio||1,2);
   if(box.width>0&&box.height>0){
    const ww=Math.max(1,Math.round(box.width*dpr)),hh=Math.max(1,Math.round(box.height*dpr));
    if(node.width!==ww||node.height!==hh){node.width=ww;node.height=hh;}
    const ctx=node.getContext('2d');if(ctx){
     if(prior&&playing&&motionAllowed&&document.visibilityState==='visible')time.current=(time.current+(now-prior)/1000*speed)%3.3;
     paintHuman(ctx,ww,hh,exercise,time.current/3.3,view);
    }
   }
   prior=now;raf.current=requestAnimationFrame(render);
  };
  raf.current=requestAnimationFrame(render);
  return()=>{cancelAnimationFrame(raf.current);};
 },[exercise,playing,motionAllowed,speed,view]);
 // update scrubber without rerendering 60 times a second
 useEffect(()=>{const id=window.setInterval(()=>setProgress(Math.round(time.current/3.3*100)),150);return()=>window.clearInterval(id);},[]);
 if(!exercise)return <div className="offline-motion-unavailable" role="alert">No offline motion preset for {name}. The written exercise instructions remain available.</div>;
 return <section className="offline-studio" aria-label={`Offline human animation for ${name}`}>
  <div className="offline-studio-head"><div><span className="offline-eyebrow">MONARCH / HUMAN MOTION LAB</span><h3>{exercise.name}</h3><p>Offline guided human demo with matched environment context · exact exercise selected</p></div><span className="offline-status">● NO INTERNET NEEDED</span></div>
  <canvas ref={canvas} className="offline-studio-canvas" role="img" aria-label={`Looping, offline guided human demonstration of ${name}, shown with the matching support or environment where possible. Use written instructions to verify exact technique.`}/>
  <div className="offline-studio-controls">
   <button type="button" onClick={()=>setPlaying(v=>!v)} aria-pressed={!playing}>{playing&&motionAllowed?'Ⅱ Pause':'▶ Play'}</button>
   <label>Motion <input aria-label="Scrub demonstration" type="range" min={0} max={100} value={progress} onChange={e=>{time.current=Number(e.target.value)/100*3.3;setProgress(Number(e.target.value));setPlaying(false);}}/></label>
   <label>View <input aria-label="Rotate human 3D viewpoint" type="range" min={-70} max={70} value={view} onChange={e=>setView(Number(e.target.value))}/></label>
   <label>Speed <select aria-label="Animation speed" value={speed} onChange={e=>setSpeed(Number(e.target.value))}><option value={0.5}>0.5×</option><option value={0.75}>0.75×</option><option value={1}>1×</option><option value={1.25}>1.25×</option></select></label>
  </div>
  <div className="offline-instructions"><div><span>HOW TO MOVE</span><p>{instructions}</p></div><div><span>CONTROL & SAFETY</span><p>{tips[movement]}</p></div></div>
  <p className="offline-disclaimer">This is a locally rendered guided human <strong>demo</strong>, not photorealistic 4K motion capture or a clinically validated biomechanics system. It now includes exercise context such as wall, bench, step, counter, band or towel where applicable. Confirm form with a qualified instructor if unsure; stop for pain.</p>
  <p className="offline-count">Offline catalog: {OFFLINE_EXERCISE_COUNT} named exercises with distinct, mapped motion presets. No YouTube, downloads, or user-uploaded videos.</p>
 </section>;
}
