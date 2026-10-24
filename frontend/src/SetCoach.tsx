import {useEffect,useState} from 'react';
import './offline-human-guide.css';

type Stage='ready'|'working'|'rest'|'between'|'done';
const DEFAULT_EXERCISE_REST=45;
function repDuration(reps:string):number{
 const seconds=reps.match(/(\d+)\s*sec/i);return seconds?Number(seconds[1]):0;
}
function approxSetTime(reps:string){const time=repDuration(reps);if(time)return time;const a=reps.match(/(\d+)[–-](\d+)/);return a?Math.round((Number(a[1])+Number(a[2]))/2*3):30;}
const timeLabel=(seconds:number)=>`${String(Math.floor(seconds/60)).padStart(2,'0')}:${String(seconds%60).padStart(2,'0')}`;
export default function SetCoach({exerciseName,sets,reps,rest}:{exerciseName:string;sets:number;reps:string;rest:number}){
 const [stage,setStage]=useState<Stage>('ready');const [setNumber,setSetNumber]=useState(1);
 const [counter,setCounter]=useState(0);const [running,setRunning]=useState(false);
 const duration=repDuration(reps);
 const [exerciseRest,setExerciseRest]=useState(DEFAULT_EXERCISE_REST);
 useEffect(()=>{setStage('ready');setSetNumber(1);setCounter(0);setRunning(false);},[exerciseName,sets,reps,rest]);
 useEffect(()=>{
  if(!running)return;
  const id=window.setInterval(()=>setCounter(n=>n+(stage==='working'?1:-1)),1000);
  return()=>window.clearInterval(id);
 },[running,stage]);
 useEffect(()=>{
  if(stage==='working'&&duration&&counter>=duration)finishSet();
  else if((stage==='rest'||stage==='between')&&counter<=0){setRunning(false);setCounter(0);setStage(stage==='between'?'done':'ready');}
  // eslint-disable-next-line react-hooks/exhaustive-deps
 },[counter,stage,duration]);
 function finishSet(){setRunning(true);if(setNumber<sets){setStage('rest');setSetNumber(n=>n+1);setCounter(rest);}else{setStage('between');setCounter(exerciseRest);}}
 function reset(){setStage('ready');setSetNumber(1);setCounter(0);setRunning(false);}
 const estimate=sets*approxSetTime(reps)+Math.max(0,sets-1)*rest+exerciseRest;
 return <div className="setcoach" aria-label={`Set and rest guide for ${exerciseName}`}>
  <div className="setcoach-head"><span>⏱ SET & RECOVERY COACH</span><strong>Approx. {Math.ceil(estimate/60)} min incl. transition</strong></div>
  <div className="setcoach-stats"><span><b>{sets}</b> sets</span><span><b>{reps}</b> target</span><span><b>{rest}s</b> between sets</span><label className="setcoach-break-label">After exercise <select value={exerciseRest} onChange={e=>setExerciseRest(Number(e.target.value))} disabled={stage!=='ready'}>{[30,45,60,90,120].map(n=><option key={n} value={n}>{n}s</option>)}</select></label></div>
  <div className="setcoach-session"><div><span>SET {Math.min(setNumber,sets)} OF {sets}</span><strong>{stage==='ready'?'Ready for next set':stage==='working'?'Perform with control':stage==='rest'?'Rest between sets':stage==='between'?'Rest before next exercise':'Session guidance finished'}</strong></div><strong className="setcoach-clock" aria-live="off">{stage==='working'&&duration?timeLabel(Math.max(0,duration-counter)):timeLabel(counter)}</strong></div>
  <div className="setcoach-actions">
   {stage==='ready'&&<button type="button" onClick={()=>{setStage('working');setCounter(0);setRunning(true);}}>▶ Start set</button>}
   {stage==='working'&&<button type="button" onClick={finishSet}>✓ Complete set</button>}
   {(stage==='working'||stage==='rest'||stage==='between')&&<button type="button" onClick={()=>setRunning(v=>!v)}>{running?'Ⅱ Pause timer':'▶ Resume timer'}</button>}
   {(stage==='rest'||stage==='between')&&<button type="button" onClick={()=>{setRunning(false);setCounter(0);setStage(stage==='rest'?'ready':'done');}}>Skip break</button>}
   <button type="button" onClick={reset}>↺ Reset</button>
  </div>
  <p>Local guidance only: repetitions are <strong>not automatically counted</strong>; tap Complete set yourself. Timers are not saved as workout history, and the displayed duration is an estimate.</p>
 </div>;
}
