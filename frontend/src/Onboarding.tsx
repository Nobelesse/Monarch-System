import { useEffect, useState } from 'react';
import './onboarding.css';

export type Module = 'workout' | 'study' | 'learning';
type Preference = { goal: string; experience: 'beginner' | 'intermediate' | 'advanced'; equipment: string[]; topics: string[] };
type Slot = { module: Module; weekday: number; minutes: number };
type OnboardingState = {
 display_name: string; timezone: string; language: 'en' | 'hi'; reduced_motion: boolean; high_contrast: boolean;
 current_step: number; completed: boolean; preferences: Partial<Record<Module, Preference>>; schedule: Slot[];
 physique: { height_cm: number | null; weight_kg: number | null };
};
type OnboardingPayload = {onboarding: OnboardingState; modules: Module[]};
const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const equipments = [
 ['bodyweight','Bodyweight'],['dumbbells','Dumbbells'],['resistance_bands','Resistance bands'],
 ['gym','Gym access'],['kettlebell','Kettlebell'],['other','Other']
] as const;
const defaultPreference = ():Preference => ({goal:'',experience:'beginner',equipment:[],topics:[]});
function csrfCookie() {return decodeURIComponent(document.cookie.split('; ').find(x=>x.startsWith('csrftoken='))?.split('=').slice(1).join('=') || '');}
async function request<T>(url:string, method='GET', body?:unknown):Promise<T> {
 if(method !== 'GET') {
  const warm = await fetch('/api/auth/csrf/',{credentials:'same-origin',cache:'no-store'});
  if(!warm.ok) throw new Error('Security initialization failed. Restart Django and reload.');
 }
 const res = await fetch(url,{method,credentials:'same-origin',cache:'no-store',
  headers:method==='GET'?{}:{'Content-Type':'application/json','X-CSRFToken':csrfCookie()},
  body:body?JSON.stringify(body):undefined});
 const contentType=res.headers.get('content-type')||'';
 if(!contentType.includes('application/json')) throw new Error(`Server returned HTTP ${res.status}, not API JSON. Check the backend terminal.`);
 const data=await res.json() as T & {error?:string};
 if(!res.ok) throw new Error(data.error||`Request failed (HTTP ${res.status})`);
 return data;
}

export default function Onboarding({userId,onCompleted}:{userId:number;onCompleted:()=>void}) {
 const [state,setState]=useState<OnboardingState|null>(null);
 const [modules,setModules]=useState<Module[]>([]);
 const [topicInputs,setTopicInputs]=useState<Partial<Record<Module,string>>>({});
 const [step,setStep]=useState(1);
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState(''); const [success,setSuccess]=useState('');
 const [loading,setLoading]=useState(true);
 useEffect(()=>{let active=true; setLoading(true); setState(null); setError('');setSuccess('');
  void request<OnboardingPayload>('/api/onboarding/').then(data=>{
   if(!active)return;
   setState(data.onboarding);setModules(data.modules);setStep(data.onboarding.current_step);
   setTopicInputs(Object.fromEntries(data.modules.map(m=>[m,(data.onboarding.preferences[m]?.topics||[]).join(', ')])));
  }).catch(err=>{if(active)setError(err instanceof Error?err.message:'Could not load onboarding.');}).finally(()=>{if(active)setLoading(false);});
  return()=>{active=false;};
 },[userId]);
 function update(values:Partial<OnboardingState>) {setState(previous=>previous?{...previous,...values}:previous);setError('');setSuccess('');}
 function preference(module:Module):Preference {return state?.preferences[module]||defaultPreference();}
 function changePreference(module:Module, change:Partial<Preference>) {
  if(!state)return;
  update({preferences:{...state.preferences,[module]:{...preference(module),...change}}});
 }
 function toggleEquipment(module:Module, equipment:string){
  const current=preference(module).equipment;
  changePreference(module,{equipment:current.includes(equipment)?current.filter(x=>x!==equipment):[...current,equipment]});
 }
 function scheduleValue(module:Module, day:number) {return state?.schedule.find(x=>x.module===module&&x.weekday===day)?.minutes||0;}
 function changeSchedule(module:Module, weekday:number, minutes:number){
  if(!state)return;
  const remaining=state.schedule.filter(x=>!(x.module===module&&x.weekday===weekday));
  update({schedule:minutes?[...remaining,{module,weekday,minutes}]:remaining});
 }
 async function save(nextStep:number, completed=false){
  if(!state || busy)return;
  setBusy(true);setError('');setSuccess('');
  try {
   const validPreferences = Object.fromEntries(modules.map(m=>[m,state.preferences[m]||defaultPreference()]));
   const data=await request<OnboardingPayload>('/api/onboarding/','PUT',{
    ...state,preferences:validPreferences,current_step:nextStep,completed
   });
   setState(data.onboarding);setModules(data.modules);setStep(data.onboarding.current_step);
   setTopicInputs(Object.fromEntries(data.modules.map(m=>[m,(data.onboarding.preferences[m]?.topics||[]).join(', ')])));
   setSuccess(completed?'Onboarding complete. Your profile is saved securely.':'Draft saved to your account.');
   if(completed) onCompleted();
  }catch(err){setError(err instanceof Error?err.message:'Unable to save.');}
  finally{setBusy(false);}
 }
 if(loading)return <section className="ob-panel"><p role="status">Loading your saved onboarding…</p></section>;
 if(!state)return <section className="ob-panel"><p role="alert" className="ob-error">{error || 'Could not load your profile.'}</p><button className="ob-action" onClick={()=>window.location.reload()}>Reload</button></section>;
 const currentPreferences=Object.fromEntries(modules.map(m=>[m,preference(m)]));
 const unscheduled=modules.filter(m=>!state.schedule.some(x=>x.module===m));
 return <div className={'ob-root '+(state.high_contrast?'ob-contrast':'')+(state.reduced_motion?' ob-reduced':'')}>
  <section className="ob-panel ob-intro">
   <span className="ob-kicker">♛ &nbsp; PLAYER INITIALIZATION · PHASE 03</span>
   <h2>{state.completed?'Edit your player profile':'Shape your next chapter.'}</h2>
   <p>These are your real goals and your available time. No invented XP, no automatic fitness advice. You stay in control.</p>
   <div className="ob-progress" role="progressbar" aria-label="Onboarding step" aria-valuenow={step} aria-valuemin={1} aria-valuemax={5}>
    {['Identity','Goals','Schedule','Privacy','Review'].map((name,i)=><button key={name} type="button" className={step===i+1?'current':step>i+1?'done':''} aria-current={step===i+1?'step':undefined} onClick={()=>{setStep(i+1);setError('');setSuccess('Unsaved changes will be saved when you continue.');}}><span>{String(i+1).padStart(2,'0')}</span>{name}</button>)}
   </div>
  </section>
  <section className="ob-panel" aria-label="Onboarding editor">
   {step===1&&<div className="ob-section"><span className="ob-kicker">01 / 05 · YOUR IDENTITY</span><h3>Who are you becoming?</h3><p className="ob-muted">You can edit these at any time. Your login username stays unchanged.</p>
    <div className="ob-form-grid"><label>Display name<input required maxLength={48} value={state.display_name} onChange={e=>update({display_name:e.target.value})}/></label>
     <label>Timezone (IANA)<input required maxLength={64} value={state.timezone} onChange={e=>update({timezone:e.target.value})} placeholder="Asia/Kolkata"/><small>Examples: Asia/Kolkata, Europe/London. Used for future schedules.</small></label>
     <label>Preferred language<select value={state.language} onChange={e=>update({language:e.target.value as 'en'|'hi'})}><option value="en">English</option><option value="hi">Hindi (preference saved; full translation is planned)</option></select></label>
    </div><div className="ob-checks"><label><input type="checkbox" checked={state.reduced_motion} onChange={e=>update({reduced_motion:e.target.checked})}/> Reduce motion effects</label>
     <label><input type="checkbox" checked={state.high_contrast} onChange={e=>update({high_contrast:e.target.checked})}/> Higher-contrast onboarding display</label></div>
   </div>}
   {step===2&&<div className="ob-section"><span className="ob-kicker">02 / 05 · YOUR GOALS</span><h3>Tell the System what matters.</h3><p className="ob-muted">Only the paths you selected on “Your paths” are shown. Goals are required when you finish onboarding.</p>
    {modules.map(m=><div className="ob-module" key={m}><div className="ob-module-top"><strong>{m==='workout'?'⚔ Workout':m==='study'?'▤ Study':'✦ Learning'}</strong><span>SELECTED PATH</span></div>
      <div className="ob-form-grid"><label>Primary goal<input value={currentPreferences[m].goal} maxLength={160} placeholder={m==='workout'?'Build a sustainable strength routine':m==='study'?'Prepare for an upcoming exam':'Learn a new technical skill'} onChange={e=>changePreference(m,{goal:e.target.value})}/></label>
       <label>Current experience<select value={currentPreferences[m].experience} onChange={e=>changePreference(m,{experience:e.target.value as Preference['experience']})}><option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option></select></label></div>
      {m==='workout'?<fieldset><legend>Equipment available (optional)</legend><div className="ob-pills">{equipments.map(([id,label])=><label key={id}><input type="checkbox" checked={currentPreferences[m].equipment.includes(id)} onChange={()=>toggleEquipment(m,id)}/>{label}</label>)}</div></fieldset>:<label className="ob-topics">{m==='study'?'Subjects':'Skills or topics'} (optional; comma-separated, max 6)<input value={topicInputs[m]??''} onChange={e=>{const raw=e.target.value;setTopicInputs(prev=>({...prev,[m]:raw}));changePreference(m,{topics:raw.split(',').map(x=>x.trim()).filter(Boolean).slice(0,6)});}} placeholder={m==='study'?'Mathematics, English':'Python, SQL'}/></label>}
     </div>)}
   </div>}
   {step===3&&<div className="ob-section"><span className="ob-kicker">03 / 05 · AVAILABLE TIME</span><h3>Build a schedule that fits real life.</h3><p className="ob-muted">Choose 15–240 minutes per day, per path. “Off” means no planned session. At least one day per path is required to complete onboarding.</p>
    {modules.map(m=><div className="ob-module" key={m}><h4>{m.toUpperCase()}</h4><div className="ob-days">{dayNames.map((name,day)=><label key={name}>{name}<select aria-label={`${m} ${name} available time`} value={scheduleValue(m,day)} onChange={e=>changeSchedule(m,day,Number(e.target.value))}><option value={0}>Off</option>{Array.from({length:16},(_,i)=>(i+1)*15).map(min=><option key={min} value={min}>{min} min</option>)}</select></label>)}</div></div>)}
    <p className="ob-muted">Total: {state.schedule.reduce((sum,x)=>sum+x.minutes,0)} minutes/week. {unscheduled.length?`${unscheduled.join(', ')} still needs a day.`:'All selected paths have scheduled time.'}</p>
   </div>}
   {step===4&&<div className="ob-section"><span className="ob-kicker">04 / 05 · PRIVACY FIRST</span><h3>Your body is not a score.</h3><p className="ob-muted">Optional inputs are stored in a separate private record. Leaving both blank deletes previous measurements. No photos, diagnosis or health predictions are generated.</p>
    {modules.includes('workout')?<div className="ob-form-grid"><label>Height (cm) — optional<input type="number" step="0.1" min="80" max="250" placeholder="Leave blank" value={state.physique.height_cm??''} onChange={e=>update({physique:{...state.physique,height_cm:e.target.value?Number(e.target.value):null}})}/></label>
     <label>Weight (kg) — optional<input type="number" step="0.1" min="20" max="350" placeholder="Leave blank" value={state.physique.weight_kg??''} onChange={e=>update({physique:{...state.physique,weight_kg:e.target.value?Number(e.target.value):null}})}/></label></div>:<p>Your current paths do not require any body measurements.</p>}
    <div className="ob-note">These values are visible only in your authenticated onboarding API. They are not included in the public status API or your basic account profile.</div>
   </div>}
   {step===5&&<div className="ob-section"><span className="ob-kicker">05 / 05 · FINAL REVIEW</span><h3>Your journey, on your terms.</h3>
    <div className="ob-review"><div><span>PLAYER</span><strong>{state.display_name||'Not set'}</strong></div><div><span>TIMEZONE</span><strong>{state.timezone}</strong></div><div><span>SELECTED PATHS</span><strong>{modules.join(' · ')}</strong></div><div><span>WEEKLY TIME</span><strong>{state.schedule.reduce((sum,x)=>sum+x.minutes,0)} minutes</strong></div></div>
    {modules.map(m=><div key={m} className="ob-review-path"><strong>{m.toUpperCase()}</strong><span>{preference(m).goal||'Goal not specified'}</span><small>{preference(m).experience} · {state.schedule.filter(x=>x.module===m).length} scheduled days</small></div>)}
    <p className="ob-muted">Finishing requires a goal and at least one day of availability for every selected path. You can revise your setup later.</p>
   </div>}
   {error&&<p className="ob-error" role="alert">{error}</p>}
   {success&&<p className="ob-success" role="status">{success}</p>}
   <div className="ob-actions"><button type="button" className="ob-outline" disabled={busy||step===1} onClick={()=>{setStep(step-1);setError('');setSuccess('');}}>← Back</button>
    <button type="button" className="ob-outline" disabled={busy} onClick={()=>void save(step,false)}>{busy?'Saving…':'Save draft'}</button>
    {step<5?<button type="button" className="ob-action" disabled={busy} onClick={()=>void save(step+1,false)}>Save & continue →</button>
     :<button type="button" className="ob-action" disabled={busy} onClick={()=>void save(5,true)}>{busy?'Saving…':'Complete onboarding ✓'}</button>}
   </div>
  </section>
 </div>;
}
