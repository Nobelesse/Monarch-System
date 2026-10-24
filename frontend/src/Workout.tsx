import {useEffect, useMemo, useState} from 'react';
import './workout.css';
import OfflineHumanGuide from './OfflineHumanGuide';
import SetCoach from './SetCoach';

type Movement = 'squat' | 'hinge' | 'push' | 'pull' | 'core' | 'mobility';
type Focus = 'balanced' | 'strength' | 'endurance' | 'mobility';
type Pace = 'easy' | 'standard';
type Exercise = {slug:string;name:string;movement:Movement;equipment:string;level:string;caution_tags:string[];instructions:string};
type Item = {id:number;position:number;sets:number;reps:string;rest_seconds:number;exercise:Exercise};
type Day = {weekday:number;day_name:string;available_minutes:number;planned_minutes:number;focus:'strength'|'mobility';theme:'upper'|'lower'|'full_body'|'recovery';items:Item[]};
type Plan = {id:number;generated_at:string;goal:string;experience:string;equipment:string[];avoid_tags:string[];focus_mode:Focus;pace:Pace;stale:boolean;days:Day[]};
type PlanReply = {plan:Plan|null;limitations?:string;reused?:boolean};
const avoidance = [
 ['knee','Knee loading'],['wrist','Wrist loading'],['floor','Floor movements'],
 ['overhead','Overhead reaching'],['impact','Impact / marching'],
] as const;
const focusOptions: {id:Focus;title:string;detail:string;icon:string}[] = [
 {id:'balanced',title:'Balanced',detail:'Variety and steady practice',icon:'◈'},
 {id:'strength',title:'Strength',detail:'A little more resistance work',icon:'⬡'},
 {id:'endurance',title:'Endurance',detail:'Controlled reps and recovery',icon:'↗'},
 {id:'mobility',title:'Mobility',detail:'More gentle movement days',icon:'✧'},
];
const repOptions=['6–8 controlled','6–10 controlled','8–12 controlled','10–15 controlled','6–8 slow','30 sec gently','10–20 sec gently'];
const restOptions=[30,45,60,75,90,120];
const movementIcons:Record<Movement,string>={squat:'▣',hinge:'⌁',push:'↗',pull:'↙',core:'◉',mobility:'✧'};
const titleCase=(s:string)=>s.replaceAll('_',' ').replace(/\b\w/g,x=>x.toUpperCase());
function csrf(){return decodeURIComponent(document.cookie.split('; ').find(x=>x.startsWith('csrftoken='))?.split('=').slice(1).join('=')||'');}
async function call<T>(url:string,method:'GET'|'POST'='GET',data?:unknown):Promise<T>{
 if(method==='POST'){
  const init=await fetch('/api/auth/csrf/',{credentials:'same-origin',cache:'no-store'});
  if(!init.ok)throw new Error('Could not initialize the security cookie. Check the Django server.');
 }
 const response=await fetch(url,{method,credentials:'same-origin',cache:'no-store',
   headers:method==='POST'?{'Content-Type':'application/json','X-CSRFToken':csrf()}:undefined,
   body:method==='POST'?JSON.stringify(data):undefined});
 if(!(response.headers.get('content-type')||'').includes('application/json'))
   throw new Error(`Unexpected HTTP ${response.status}. Check the Django backend and Vite proxy.`);
 const body=await response.json() as T & {error?:string};
 if(!response.ok)throw new Error(body.error||`API failed (HTTP ${response.status})`);
 return body;
}

export default function Workout({userId,onOpenOnboarding}:{userId:number;onOpenOnboarding:()=>void}){
 const [plan,setPlan]=useState<Plan|null>(null);
 const [library,setLibrary]=useState<Exercise[]>([]);
 const [avoid,setAvoid]=useState<string[]>([]);
 const [focus,setFocus]=useState<Focus>('balanced');
 const [pace,setPace]=useState<Pace>('standard');
 const [ack,setAck]=useState(false);
 const [loading,setLoading]=useState(true);
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState('');
 const [notice,setNotice]=useState('');
 const [selectedDay,setSelectedDay]=useState<number|null>(null);
 const [openSwap,setOpenSwap]=useState<number|null>(null);
 const [alternatives,setAlternatives]=useState<Exercise[]>([]);
 const [editId,setEditId]=useState<number|null>(null);
 const [editSets,setEditSets]=useState(2);
 const [editReps,setEditReps]=useState('6–10 controlled');
 const [editRest,setEditRest]=useState(75);
 const [query,setQuery]=useState('');
 const [movementFilter,setMovementFilter]=useState<'all'|Movement>('all');
 const [equipmentFilter,setEquipmentFilter]=useState('all');
 const [section,setSection]=useState<'plan'|'library'>('plan');
 const [motionId,setMotionId]=useState<number|null>(null);
 const [codexMotion,setCodexMotion]=useState<string|null>(null);
 useEffect(()=>{
  let live=true;setLoading(true);setError('');setPlan(null);setSelectedDay(null);
  void Promise.all([call<PlanReply>('/api/workout/plan/'),call<{exercises:Exercise[]}>('/api/workout/library/')])
   .then(([p,l])=>{if(!live)return;
    setPlan(p.plan);setLibrary(l.exercises);setAvoid(p.plan?.avoid_tags||[]);
    setFocus(p.plan?.focus_mode||'balanced');setPace(p.plan?.pace||'standard');
    setSelectedDay(p.plan?.days[0]?.weekday??null);
   }).catch(e=>{if(live)setError(e instanceof Error?e.message:'Workout could not load.');})
   .finally(()=>{if(live)setLoading(false);});
  return ()=>{live=false;};
 },[userId]);
 const day=plan?.days.find(d=>d.weekday===selectedDay)??plan?.days[0];
 const equipmentOptions=useMemo(()=>Array.from(new Set(library.map(x=>x.equipment))).sort(),[library]);
 const matches=useMemo(()=>library.filter(x=>
  (movementFilter==='all'||x.movement===movementFilter) &&
  (equipmentFilter==='all'||x.equipment===equipmentFilter) &&
  (x.name+' '+x.instructions+' '+x.movement).toLowerCase().includes(query.trim().toLowerCase())
 ),[library,movementFilter,equipmentFilter,query]);
 const strengthDays=plan?.days.filter(d=>d.focus==='strength').length??0;
 const minutes=plan?.days.reduce((sum,d)=>sum+d.planned_minutes,0)??0;
 const differences=!!plan&&(focus!==plan.focus_mode||pace!==plan.pace||JSON.stringify([...avoid].sort())!==JSON.stringify([...plan.avoid_tags].sort()));
 const resetAlert=()=>{setError('');setNotice('');};
 async function generate(regenerate=false){if(busy)return;setBusy(true);resetAlert();setOpenSwap(null);setEditId(null);
  try{
   const r=await call<PlanReply>('/api/workout/plan/generate/','POST',{
    avoid_tags:avoid,acknowledged:ack,regenerate,focus_mode:focus,pace
   });
   setPlan(r.plan);setSelectedDay(r.plan?.days[0]?.weekday??null);
   setNotice(r.reused?'Matching draft retained.':'Personalized weekly draft saved to your account.');
  }catch(e){setError(e instanceof Error?e.message:'Could not generate your draft.');}
  finally{setBusy(false);}
 }
 async function reload(){const result=await call<PlanReply>('/api/workout/plan/');setPlan(result.plan);}
 async function showAlternatives(item:Item){resetAlert();setEditId(null);
  if(openSwap===item.id){setOpenSwap(null);return;}
  try{const data=await call<{alternatives:Exercise[]}>(`/api/workout/items/${item.id}/alternatives/`);
   setAlternatives(data.alternatives);setOpenSwap(item.id);
  }catch(e){setError(e instanceof Error?e.message:'Unable to fetch alternatives.');}
 }
 async function replace(item:Item,slug:string){setBusy(true);resetAlert();
  try{await call(`/api/workout/items/${item.id}/substitute/`,'POST',{exercise_slug:slug});
   await reload();setOpenSwap(null);setNotice('Exercise replacement saved.');
  }catch(e){setError(e instanceof Error?e.message:'Replacement failed.');}
  finally{setBusy(false);}
 }
 function startEdit(item:Item){setEditId(item.id);setOpenSwap(null);setEditSets(item.sets);setEditReps(item.reps);setEditRest(item.rest_seconds);resetAlert();}
 async function saveEdit(item:Item){setBusy(true);resetAlert();
  try{await call(`/api/workout/items/${item.id}/adjust/`,'POST',{sets:editSets,reps:editReps,rest_seconds:editRest});
   await reload();setEditId(null);setNotice('Your prescription changes were saved.');
  }catch(e){setError(e instanceof Error?e.message:'Could not save changes.');}
  finally{setBusy(false);}
 }
 async function move(item:Item,direction:'up'|'down') {setBusy(true);resetAlert();
  try{const r=await call<{plan:Plan}>(`/api/workout/items/${item.id}/move/`,'POST',{direction});
   setPlan(r.plan);setNotice('Exercise order saved.');
  }catch(e){setError(e instanceof Error?e.message:'Could not move this exercise.');}
  finally{setBusy(false);}
 }
 return <div className="wk-root">
  <section className="wk-command wk-cinematic-command" aria-label="Workout command center"><div className="wk-scene-world" aria-hidden="true"/><div className="wk-scene-haze" aria-hidden="true"/>
   <div className="wk-command-copy"><span className="wk-eyebrow">MONARCH SYSTEM / TRAINING MODULE</span>
    <h2>Forge your<br/><em>own strength.</em></h2>
    <p>A deliberate training system built around your time, available equipment and selected approach. Real progress comes from consistent practice—not a generated rank.</p>
    <div className="wk-hero-actions"><button type="button" onClick={()=>setSection('plan')} className="wk-primary">{plan?'Open weekly draft ↗':'Create training draft ↗'}</button><button className="wk-outline" onClick={onOpenOnboarding}>Edit player profile</button></div>
   </div>
   <div className="wk-world-caption" aria-hidden="true">THE TRAINING SANCTUARY <span>YOUR PACE · YOUR PATH</span></div>
  </section>
  <section className="wk-stats" aria-label="Your saved workout draft statistics">
   <div><span>WEEKLY SESSIONS</span><strong>{plan?.days.length??'—'}</strong><small>Saved scheduled days</small></div>
   <div><span>STRENGTH DAYS</span><strong>{plan?strengthDays:'—'}</strong><small>Nonadjacent days</small></div>
   <div><span>PLANNED TIME</span><strong>{plan?minutes+'m':'—'}</strong><small>Suggestions, not logged</small></div>
   <div><span>PLAN STATUS</span><strong className={plan?.stale?'wk-caution':''}>{plan?(plan.stale?'STALE':'READY'):'NOT SET'}</strong><small>Private draft, no XP</small></div>
  </section>
  <div className="wk-tabbar" role="tablist" aria-label="Workout views">
   <button type="button" role="tab" aria-selected={section==='plan'} className={section==='plan'?'active':''} onClick={()=>setSection('plan')}>⚔ Training planner</button>
   <button type="button" role="tab" aria-selected={section==='library'} className={section==='library'?'active':''} onClick={()=>setSection('library')}>◇ Exercise codex <span>{library.length}</span></button>
  </div>
  {error&&<div role="alert" className="wk-banner wk-error">{error}</div>}
  {notice&&<div role="status" className="wk-banner wk-success">{notice}</div>}
  {loading&&<div className="wk-panel" role="status">Loading your Workout space…</div>}
  {!loading&&section==='plan'&&<>
   <section className="wk-panel wk-config"><div className="wk-heading"><div><span className="wk-eyebrow">01 / GENERATOR SETTINGS</span><h3>Set your training intention</h3><p>Choose an explicit focus. Your written onboarding goal is displayed with the plan, but is not interpreted as medical or AI guidance.</p></div><button className="wk-outline" onClick={onOpenOnboarding}>Onboarding ↗</button></div>
    <div className="wk-focus-grid" role="group" aria-label="Training focus">
     {focusOptions.map(option=><button key={option.id} type="button" className={'wk-focus '+(focus===option.id?'selected':'')} aria-pressed={focus===option.id} onClick={()=>setFocus(option.id)}>
      <span className="wk-focus-icon">{option.icon}</span><strong>{option.title}</strong><small>{option.detail}</small></button>)}
    </div>
    <div className="wk-controls"><div><label htmlFor="wk-pace">Training pace</label><select id="wk-pace" value={pace} onChange={e=>setPace(e.target.value as Pace)}><option value="standard">Standard — within saved schedule</option><option value="easy">Easy — fewer sets, shorter sessions</option></select></div>
    <div><span className="wk-label">Movement exclusions</span><p className="wk-help">Broad preference filters only—not medical clearance.</p><div className="wk-tags">{avoidance.map(([tag,title])=><label key={tag} className={avoid.includes(tag)?'selected':''}><input type="checkbox" checked={avoid.includes(tag)} onChange={e=>setAvoid(current=>e.target.checked?[...current,tag]:current.filter(x=>x!==tag))}/>{title}</label>)}</div></div></div>
    <div className="wk-safety"><strong>Safety first.</strong> These are general activity drafts, not injury screening or treatment. Stop for pain, faintness or dizziness. Seek qualified advice if exercise could pose a health risk.</div>
    <label className="wk-ack"><input type="checkbox" checked={ack} onChange={e=>setAck(e.target.checked)}/><span>I understand these limitations and will review every suggestion before attempting it.</span></label>
    <div className="wk-actionbar"><button className="wk-primary" type="button" disabled={busy||!ack} onClick={()=>void generate(Boolean(plan))}>{busy?'Saving…':plan?'Regenerate selected draft ↻':'Generate my weekly draft ↗'}</button>
     <span>{differences?'Settings changed. Regenerate to apply them.':'Regeneration replaces the current draft; actual workout history starts in Phase 5.'}</span></div>
   </section>
   {plan&&<section className="wk-panel wk-program"><div className="wk-heading"><div><span className="wk-eyebrow">02 / SAVED WEEKLY PROGRAM</span><h3>Your training schedule</h3><p>{plan.goal} · {titleCase(plan.experience)} · {titleCase(plan.focus_mode)} focus · {titleCase(plan.pace)} pace</p></div><span className="wk-chip">{plan.days.length} SESSIONS</span></div>
    {plan.stale&&<div role="alert" className="wk-banner wk-error">Onboarding changed after this draft was created. Regenerate before editing.</div>}
    <div className="wk-day-nav" role="group" aria-label="Choose workout day">{plan.days.map(d=><button key={d.weekday} type="button" aria-pressed={day?.weekday===d.weekday} className={day?.weekday===d.weekday?'active':''} onClick={()=>{setSelectedDay(d.weekday);setEditId(null);setOpenSwap(null);setMotionId(null);}}><small>{d.day_name.slice(0,3).toUpperCase()}</small><strong>{d.focus==='strength'?'⚔':'✧'}</strong><span>{titleCase(d.theme).replace('Full Body','Full body')}</span></button>)}</div>
    {day&&<div className="wk-active-day"><div className="wk-day-intro"><div><span className="wk-eyebrow">{day.focus==='strength'?'STRENGTH SESSION':'RECOVERY / GENTLE MOVEMENT'}</span><h4>{day.day_name} <span>· {titleCase(day.theme)}</span></h4><p>{day.planned_minutes} suggested minutes from {day.available_minutes} available. Include a comfortable warm-up and cool-down.</p></div><span className="wk-big-index">{String(day.weekday+1).padStart(2,'0')}</span></div>
     <div className="wk-exercise-list">{day.items.map((item,index)=><article className="wk-exercise" key={item.id}>
      <div className="wk-exercise-icon" aria-hidden="true">{movementIcons[item.exercise.movement]}</div>
      <div className="wk-exercise-main"><div className="wk-exercise-head"><div><small>MOVE {String(index+1).padStart(2,'0')} · {titleCase(item.exercise.movement)}</small><h5 className="wk-name-with-demo">{item.exercise.name}<button type="button" className="wk-motion-open" aria-expanded={motionId===item.id} onClick={()=>setMotionId(motionId===item.id?null:item.id)}>{motionId===item.id?"✕ Close offline demo":"▶ OFFLINE 3D HUMAN DEMO"}</button></h5></div><span className="wk-chip">{titleCase(item.exercise.equipment)}</span></div>
       <p>{item.exercise.instructions}</p><div className="wk-dose"><span><b>{item.sets}</b> sets</span><span><b>{item.reps}</b> reps / duration</span><span><b>{item.rest_seconds}s</b> rest</span></div>
       <SetCoach exerciseName={item.exercise.name} sets={item.sets} reps={item.reps} rest={item.rest_seconds}/>
       <div className="wk-item-actions"><button type="button" disabled={busy||plan.stale} onClick={()=>startEdit(item)}>✎ Adjust</button><button type="button" disabled={busy||plan.stale} onClick={()=>void showAlternatives(item)}>⇄ Swap</button>
        <button type="button" aria-label={'Move '+item.exercise.name+' up'} disabled={busy||plan.stale||index===0} onClick={()=>void move(item,'up')}>↑</button><button type="button" aria-label={'Move '+item.exercise.name+' down'} disabled={busy||plan.stale||index===day.items.length-1} onClick={()=>void move(item,'down')}>↓</button></div>
       {motionId===item.id&&<OfflineHumanGuide slug={item.exercise.slug} name={item.exercise.name} movement={item.exercise.movement} instructions={item.exercise.instructions}/>}
       {editId===item.id&&<div className="wk-editor"><strong>Adjust suggested prescription</strong><div><label>Sets<select value={editSets} onChange={e=>setEditSets(Number(e.target.value))}>{[1,2,3,4].filter(x=>day.focus!=='mobility'||x<=2).map(x=><option key={x} value={x}>{x}</option>)}</select></label><label>Repetitions / duration<select value={editReps} onChange={e=>setEditReps(e.target.value)}>{repOptions.map(x=><option key={x}>{x}</option>)}</select></label><label>Rest seconds<select value={editRest} onChange={e=>setEditRest(Number(e.target.value))}>{restOptions.map(x=><option key={x} value={x}>{x}s</option>)}</select></label></div><button type="button" className="wk-primary" disabled={busy} onClick={()=>void saveEdit(item)}>Save changes</button><button type="button" className="wk-outline" onClick={()=>setEditId(null)}>Cancel</button></div>}
       {openSwap===item.id&&<div className="wk-editor wk-alternatives"><strong>Permitted alternatives · same movement family</strong>{alternatives.length===0?<p>No matching alternatives available.</p>:<div className="wk-alt-list">{alternatives.map(a=><button key={a.slug} type="button" disabled={busy} onClick={()=>void replace(item,a.slug)}><strong>{a.name}</strong><small>{titleCase(a.equipment)} · {a.instructions}</small></button>)}</div>}<button className="wk-outline" type="button" onClick={()=>setOpenSwap(null)}>Close</button></div>}
      </div>
     </article>)}</div>
    </div>}
    <p className="wk-footnote">Training draft only. No workout completion, weight tracking, streaks, or XP is inferred from this plan.</p>
   </section>}
  </>}
  {!loading&&section==='library'&&<section className="wk-panel wk-codex"><div className="wk-heading"><div><span className="wk-eyebrow">EXERCISE CODEX / CURATED LIBRARY</span><h3>Discover your next movement</h3><p>{library.length} instructional entries. Available equipment and restrictions determine whether an exercise can appear in a personal draft.</p></div><span className="wk-chip">{matches.length} MATCHES</span></div>
   <div className="wk-search-row"><label>Search exercises<input type="search" placeholder="e.g. band row, squat, shoulder…" value={query} onChange={e=>setQuery(e.target.value)}/></label>
    <label>Movement<select value={movementFilter} onChange={e=>setMovementFilter(e.target.value as 'all'|Movement)}><option value="all">All movements</option>{(['squat','hinge','push','pull','core','mobility'] as Movement[]).map(x=><option key={x} value={x}>{titleCase(x)}</option>)}</select></label>
    <label>Equipment<select value={equipmentFilter} onChange={e=>setEquipmentFilter(e.target.value)}><option value="all">All equipment</option>{equipmentOptions.map(x=><option value={x} key={x}>{titleCase(x)}</option>)}</select></label>
   </div>
   <div className="wk-codex-grid">{matches.map(e=><article key={e.slug}><div className="wk-codex-icon">{movementIcons[e.movement]}</div><small>{titleCase(e.movement)} · {titleCase(e.level)}</small><h4>{e.name}</h4><p>{e.instructions}</p><small className="wk-offline-hint">Offline motion preview for this exact exercise • Personal sets and recovery appear in your generated plan</small><button type="button" className="wk-outline" aria-expanded={codexMotion===e.slug} onClick={()=>setCodexMotion(codexMotion===e.slug?null:e.slug)}>{codexMotion===e.slug?'Hide offline demo':'▶ Offline 3D human demo'}</button>{codexMotion===e.slug&&<OfflineHumanGuide slug={e.slug} name={e.name} movement={e.movement} instructions={e.instructions}/>}<div><span>{titleCase(e.equipment)}</span>{e.caution_tags.map(t=><span key={t}>{t} caution</span>)}</div></article>)}</div>
   {matches.length===0&&<p className="wk-muted">No exercises match those filters. Try broadening the search.</p>}
  </section>}
 </div>;
}
