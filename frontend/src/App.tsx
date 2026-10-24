import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react';
import Onboarding from './Onboarding';
import Workout from './Workout';
import abyssWorld from './assets/abyss-world.webp';

type Module = 'workout' | 'study' | 'learning';
type Page = 'Overview' | 'Your paths' | 'Onboarding' | 'Workout' | 'Account' | 'Roadmap' | 'System status';
type Health = {status:string; api:string; database:string; version:string};
type System = {google_login_configured:boolean; google_client_id:string};
type Player = {id:number; username:string; email:string; modules:Module[]; is_staff:boolean};
type GoogleCredential = { credential: string };
type GoogleAPI = {accounts:{id:{initialize:(options:{client_id:string;callback:(x:GoogleCredential)=>void})=>void;renderButton:(node:HTMLElement,options:Record<string,unknown>)=>void}}};
declare global {interface Window { google?:GoogleAPI }}
const paths: {id:Module; title:string; tag:string; text:string; icon:string; phase:string}[] = [
 {id:'workout',title:'Build your strength',tag:'BODY',text:'A training journey built around your ability, equipment and recovery.',icon:'↟',phase:'Workout engine · Phase 4 available'},
 {id:'study',title:'Sharpen your focus',tag:'MIND',text:'Give your study goals structure, one focused session at a time.',icon:'▤',phase:'Study sessions · Phase 7'},
 {id:'learning',title:'Expand your world',tag:'SKILL',text:'Turn curiosity into practice and build skills that stay with you.',icon:'✧',phase:'Learning paths · Phase 7'},
];
const phases = ['Foundation & setup','Accounts & access','Player onboarding','Workout engine','Workout execution','Quests, XP & ranks','Study & learning','Adaptive plans & insights','Mobile installation & QR','Reliability & release'];
function initialModules(): Module[] {
 try {const saved:unknown=JSON.parse(localStorage.getItem('monarch.modules.v1') || '["workout"]');
 if(Array.isArray(saved)){const valid=saved.filter((x):x is Module=>['workout','study','learning'].includes(x));if(valid.length)return [...new Set(valid)];}} catch { /* defaults */ }
 return ['workout'];
}
function csrfCookie() {return decodeURIComponent(document.cookie.split('; ').find(x=>x.startsWith('csrftoken='))?.split('=').slice(1).join('=') || '');}
// The proxy, a CSRF rejection, or a missing Django server can return HTML.
// Never display a raw JSON parser exception to the player.
async function apiResponse<T>(response:Response, endpoint:string):Promise<T> {
 const contentType=response.headers.get('content-type') || '';
 if(!contentType.toLowerCase().includes('application/json')) {
  if(response.status===403) throw new Error('Request blocked (HTTP 403). Reload the page and try again. If it continues, verify the Django server and CSRF configuration.');
  if(response.status===404) throw new Error(`API route missing (HTTP 404): ${endpoint}. Check that the Django backend is running on port 8000.`);
  throw new Error(`Unexpected response (HTTP ${response.status}) from ${endpoint}. Check the Django backend terminal and Vite proxy; the server returned a web page instead of API JSON.`);
 }
 const body:unknown=await response.json();
 if(!response.ok) {
  const error=body && typeof body==='object' && 'error' in body && typeof body.error==='string' ? body.error : `Request failed (HTTP ${response.status}).`;
  throw new Error(error);
 }
 return body as T;
}
async function api<T>(url:string, method='GET', data?:object):Promise<T> {
 if(method!=='GET') {
  const csrfResponse=await fetch('/api/auth/csrf/', {credentials:'same-origin',cache:'no-store'});
  await apiResponse<{csrf:string}>(csrfResponse, '/api/auth/csrf/');
  if(!csrfCookie()) throw new Error('Security cookie missing. Open Monarch at http://127.0.0.1:5173/ and reload.');
 }
 const res=await fetch(url,{method,credentials:'same-origin',cache:'no-store',headers:method==='GET'?{}:{'Content-Type':'application/json','X-CSRFToken':csrfCookie()},body:data?JSON.stringify(data):undefined});
 return apiResponse<T>(res,url);
}


// React StrictMode mounts effects twice in development. Share one reset promise
// so a late duplicate logout cannot invalidate a fresh login.
let initialLogout:Promise<void>|undefined;
function clearPreviousLogin():Promise<void>{
 if(!initialLogout)initialLogout=api('/api/auth/logout/','POST').then(()=>{}).catch(()=>{});
 return initialLogout;
}
export default function App(){
 const [page,setPage]=useState<Page>('Account');
 const [modules,setModules]=useState<Module[]>(initialModules);
 const [player,setPlayer]=useState<Player|null>(null);
 const [authBooting,setAuthBooting]=useState(true);
 const [onboardingComplete,setOnboardingComplete]=useState(false);
 const [authMode,setAuthMode]=useState<'login'|'register'>('login');
 const [identity,setIdentity]=useState(''); const [email,setEmail]=useState(''); const [password,setPassword]=useState('');
 const [health,setHealth]=useState<Health|null>(null); const [system,setSystem]=useState<System|null>(null);
 const [busy,setBusy]=useState(false);const [authBusy,setAuthBusy]=useState(false);const [message,setMessage]=useState('');const [error,setError]=useState('');
 const googleContainer=useRef<HTMLDivElement>(null);
 const setAccount=async(user:Player)=>{
  setPlayer(user);setModules(user.modules);setPassword('');setMessage('Welcome, '+user.username+'.');
  // The completion flag comes from Django, never stale local browser storage.
  try{
   const result=await api<{onboarding:{completed:boolean}}>('/api/onboarding/');
   setOnboardingComplete(result.onboarding.completed);
   setPage(result.onboarding.completed?'Overview':'Onboarding');
  }catch{
   setOnboardingComplete(false);setPage('Onboarding');
   setMessage('Signed in. Onboarding status could not be checked; open Onboarding to retry.');
  }
 };
 const check=useCallback(async()=>{setBusy(true);setError('');try{const response=await fetch('/api/health/',{signal:AbortSignal.timeout(8000),cache:'no-store'});const data=await response.json() as Health;if(!data.api || !data.database)throw new Error();setHealth(data);}catch{setHealth(null);setError('Backend not reachable. Start scripts/backend.ps1, then check again.');}finally{setBusy(false);}},[]);
 useEffect(()=>{
  void check();void api<System>('/api/system/').then(setSystem).catch(()=>{});
  // Explicit fresh-start sign-in: invalidate any stale server session at page load,
  // including browser restores and full refreshes. Never auto-restore /me/.
  // HTTP 401 simply means there was no earlier session to clear.
  void clearPreviousLogin().finally(()=>setAuthBooting(false));
 },[check]);
 const googleAction=useCallback(async(credential:string)=>{if(authBooting)return;setAuthBusy(true);setError('');try{
  const url=player?'/api/auth/google/link/':'/api/auth/google/';
  if(player){await api(url,'POST',{credential});setMessage('Your Google account is now linked.');}
  else{const result=await api<{user:Player}>(url,'POST',{credential});await setAccount(result.user);}
 }catch(e){setError(e instanceof Error?e.message:'Google sign-in failed.');}finally{setAuthBusy(false);}},[player,authBooting]);
 useEffect(()=>{if(page!=='Account'||!system?.google_login_configured||!googleContainer.current)return;
  let cancelled=false; const scriptId='monarch-google-identity';
  const draw=()=>{if(cancelled||!window.google||!googleContainer.current)return;googleContainer.current.replaceChildren();window.google.accounts.id.initialize({client_id:system.google_client_id,callback:x=>void googleAction(x.credential)});window.google.accounts.id.renderButton(googleContainer.current,{theme:'filled_black',size:'large',text:player?'continue_with':'signin_with',shape:'rectangular'});};
  if(window.google){draw();return()=>{cancelled=true;};}
  let script=document.getElementById(scriptId) as HTMLScriptElement|null;
  if(!script){script=document.createElement('script');script.id=scriptId;script.src='https://accounts.google.com/gsi/client';script.async=true;document.head.appendChild(script);}
  script.addEventListener('load',draw);
  return()=>{cancelled=true;script?.removeEventListener('load',draw);};
 },[page,system,player,googleAction]);
 function toggle(id:Module){setMessage('');if(modules.includes(id)&&modules.length===1){setMessage('Keep at least one path selected.');return;}setModules(modules.includes(id)?modules.filter(x=>x!==id):[...modules,id]);}
 async function save(){setMessage('');setError('');try{if(player){const result=await api<{modules:Module[]}>('/api/paths/','PUT',{modules});setPlayer({...player,modules:result.modules});setMessage('Saved securely to your account.');}
 else{localStorage.setItem('monarch.modules.v1',JSON.stringify(modules));setMessage('Saved on this browser. Sign up to protect and sync your choices.');}}catch(e){setError(e instanceof Error?e.message:'Could not save paths.');}}
 async function submitAuth(e:FormEvent<HTMLFormElement>){e.preventDefault();if(authBooting||authBusy)return;setAuthBusy(true);setError('');setMessage('');try{
  const result=authMode==='register'
   ?await api<{user:Player}>('/api/auth/register/','POST',{username:identity,email,password,modules})
   :await api<{user:Player}>('/api/auth/login/','POST',{identifier:identity,password});
  await setAccount(result.user);
 }catch(e){setError(e instanceof Error?e.message:'Could not sign in.');}finally{setAuthBusy(false);}}
 async function signOut(){setAuthBusy(true);setError('');try{await api('/api/auth/logout/','POST');setPlayer(null);setOnboardingComplete(false);setModules(initialModules());setPassword('');setPage('Account');setMessage('You have signed out.');setAuthMode('login');}catch(e){setError(e instanceof Error?e.message:'Could not sign out.');}finally{setAuthBusy(false);}}
 const online=health?.database==='connected';
 const navigate=(p:Page)=>{setPage(p);setMessage('');setError('');};
 return <div className="app"><aside><a className="brand" href="#" onClick={e=>{e.preventDefault();navigate('Overview');}}><span className="brand-icon">♜</span><span>MONARCH<small>THE SYSTEM WITHIN</small></span></a><div className="nav-label">YOUR COMMAND CENTER</div><nav aria-label="Main navigation">{(['Overview','Your paths','Onboarding','Workout','Account','Roadmap','System status'] as Page[]).map((p,i)=><button key={p} className={page===p?'active':''} onClick={()=>navigate(p)}><span aria-hidden="true">{['◈','⌘','✦','⚔','♙','◇','◎'][i]}</span>{p}{page===p&&<b>•</b>}</button>)}</nav><div className="sidebar-note abyss-sidebar-card"><span className="eyebrow">THE FIRST STEP</span><p>Consistency is your<br/>strongest ability.</p><span className="muted">A stronger version of you begins here.</span><span className="sidebar-glow" aria-hidden="true" /></div><div className="build-tag"><span className="dot"/> LOCAL DEVELOPMENT <small>v0.4.3 · Cinematic UI</small></div></aside><div className="workspace"><div className="ambient-particles" aria-hidden="true"/><header><span>PLAYER SPACE <span className="slash">/</span> <strong>{page}</strong></span><div className="header-actions"><button className="account-chip" onClick={()=>navigate('Account')}>{player?'♙ '+player.username:'Sign in / Register'}</button><button className="status-pill" onClick={()=>navigate('System status')}><span className={'dot '+(!online?'amber':'')}/>{busy?'Checking system':online?'System connected':'Setup required'}</button></div></header><main className={"page-main page-"+page.toLowerCase().replaceAll(" ","-")}><div className="heading"><div><span className="eyebrow">MONARCH SYSTEM / V0.4.3 · ABYSS EXPERIENCE</span><h1>{page==='Overview'?'Your journey starts here.':page==='Your paths'?'Choose your direction.':page==='Onboarding'?'Initialize your player.':page==='Workout'?'Forge your training plan.':page==='Account'?player?'Your player account.':'Enter the System.':page==='Roadmap'?'Built one milestone at a time.':'Know your system.'}</h1><p className="muted">{page==='Overview'?'Real effort. Lasting progress. A stronger version of you.':page==='Your paths'?'One path or all three. Make the System your own.':page==='Onboarding'?'Your goals, your pace and your rules.':page==='Workout'?'Conservative exercise options based on your preferences.':page==='Account'?'Your progress belongs to you.':page==='Roadmap'?'A clear view of what works now and what comes next.':'Live connection checks for your local development environment.'}</p></div><span className="release">WORKOUT ENGINE <b>04 / 10</b></span></div>
 {page==='Overview'&&<><section className="hero cinematic-home" aria-label="Monarch world overview">
 <div className="cinematic-world" role="img" aria-label="Violet-lit abyssal citadel with a lone traveler facing a glowing portal"><img src={abyssWorld} alt="" /></div>
 <div className="cinematic-fog" aria-hidden="true"/><div className="cinematic-sparks" aria-hidden="true"/><div className="cinematic-shade" aria-hidden="true"/>
 <div className="hero-copy"><span className="hero-kicker">✧ &nbsp; THE ABYSS AWAKENS</span><h2>Your journey<br/><em>starts here.</em></h2><p>Real effort. Lasting progress.<br/>A stronger version of you.</p><button className="primary" onClick={()=>navigate(player?(onboardingComplete?(modules.includes('workout')?'Workout':'Your paths'):'Onboarding'):'Account')}>{player?(onboardingComplete?'Continue your path':'Complete your onboarding'):'Begin your awakening'} <span>→</span></button><span className="hero-note">{player?'Welcome back, '+player.username:'Create an account to save your own journey'}</span></div>
 <div className="hero-sidecard"><span className="eyebrow">MONARCH ENGINE <b>04 / 10</b></span><div className="hero-progress-track"><span style={{width:'40%'}}/></div><small>CURRENT MILESTONE</small><strong>Build your foundation</strong><p>{player?(onboardingComplete?'Your training draft is ready to explore.':'Complete onboarding to unlock personal training drafts.'):'Choose your paths and start with your own goals.'}</p><button type="button" onClick={()=>navigate(player?'Workout':'Account')} aria-label="Open next milestone">↗</button></div>
 <div className="cinematic-caption">✦ &nbsp; A WORLD BUILT AROUND REAL PROGRESS <span>LOCAL FIRST · PRIVATE BY DEFAULT</span></div>
 </section><div className="metrics abyss-metrics"><div><span className="metric-orb">♧</span><span className="eyebrow">SELECTED PATHS</span><strong>{String(modules.length).padStart(2,'0')} <small>/ 03</small></strong><span>{player?'Synced to your profile':'Your starting selection'}</span></div><div><span className="metric-orb">✧</span><span className="eyebrow">ONBOARDING</span><strong>{player?(onboardingComplete?'Complete':'In progress'):'Not started'}</strong><span>{player?'Your preferences stay saved':'Sign in to start'}</span></div><div><span className="metric-orb">⚔</span><span className="eyebrow">WORKOUT MODULE</span><strong>Available</strong><span>Training drafts · No fabricated stats</span></div><div><span className="metric-orb">◈</span><span className="eyebrow">SYSTEM STATUS</span><strong className={online?'green':''}>{online?'Connected':'Offline'}</strong><span>{online?'API + database available':'Check local services'}</span></div></div>
 <div className="section-heading"><h2>Three paths. One evolution.</h2><button className="text-button" onClick={()=>navigate('Your paths')}>Manage paths ↗</button></div><div className="path-grid">{paths.map(p=><button className={'path-card '+p.id} key={p.id} onClick={()=>navigate('Your paths')}><div className="card-top"><span className="path-icon">{p.icon}</span><span className="mini-tag">{modules.includes(p.id)?'SELECTED':'EXPLORE'}</span></div><span className="eyebrow">{p.tag}</span><h3>{p.title}</h3><p>{p.text}</p><div className="card-bottom">{p.phase}<span>↗</span></div></button>)}</div><div className="notice"><span>◇</span><p><strong>Your command center is growing.</strong> Personalize your player with real goals, time and preferences. Workout drafts are now available. Execution, quests and XP arrive in later phases.</p><button className="text-button" onClick={()=>navigate('Roadmap')}>View roadmap →</button></div></>}
 {page==='Your paths'&&<><section className="panel"><span className="eyebrow">MAKE IT PERSONAL</span><h2>What do you want to work on?</h2><p className="muted">{player?'Saved choices are tied to your signed-in account.':'Preview choices stay in this browser. Create an account to sync them securely.'}</p><div className="path-grid selections">{paths.map(p=><label className={'path-card '+p.id+(modules.includes(p.id)?' selected':'')} key={p.id}><div className="card-top"><span className="path-icon">{p.icon}</span><input type="checkbox" checked={modules.includes(p.id)} onChange={()=>toggle(p.id)} aria-label={'Enable '+p.id}/></div><span className="eyebrow">{p.tag}</span><h3>{p.title}</h3><p>{p.text}</p></label>)}</div><button className="primary" onClick={()=>void save()}>Save my paths <span>✓</span></button><p role="status" className="feedback">{message}</p>{error&&<p role="alert" className="auth-error">{error}</p>}</section><section className="panel secondary"><h2>Your body is more than a number.</h2><p>Workout onboarding will consider goals, experience, equipment, available time and limitations—not just height or weight. Training progression will follow performance and recovery, independently of game XP.</p><button className="primary" onClick={()=>navigate('Onboarding')}>Open onboarding ↗</button></section></>}
 {page==='Onboarding'&&(player?<Onboarding userId={player.id} onCompleted={()=>{setOnboardingComplete(true);navigate('Overview');setMessage('Player onboarding saved.');}}/>:<section className="panel"><h2>Sign in to initialize your player.</h2><p className="muted">Onboarding data is saved privately to your account, not this browser.</p><button className="primary" onClick={()=>navigate('Account')}>Sign in or register ↗</button></section>)}
 {page==='Workout'&&(player?<Workout userId={player.id} onOpenOnboarding={()=>navigate('Onboarding')}/>:<section className="panel"><h2>Sign in to access Workout.</h2><button className="primary" onClick={()=>navigate('Account')}>Sign in ↗</button></section>)}
 {page==='Account'&&<section className="account-stage"><div className="account-visual"><div className="account-visual-world"/><span className="eyebrow">THE SYSTEM IS CALLING</span><h2>Discipline.<br/>Progress.<br/><em>A stronger you.</em></h2><p>Your player story begins with a decision.</p></div><div className="panel account-panel"><span className="eyebrow">SECURE PLAYER ACCESS</span>{player?<><h2>Welcome, {player.username}.</h2><p className="muted">Your account stores your selected paths privately. Other players cannot read or edit them.</p><div className="account-details"><div><span>PLAYER ID</span><strong>#{player.id}</strong></div><div><span>USERNAME</span><strong>{player.username}</strong></div><div><span>EMAIL</span><strong>{player.email}</strong></div><div><span>PATHS</span><strong>{player.modules.join(' · ')}</strong></div></div>{system?.google_login_configured?<><p className="muted">Optional: link your existing account with the same verified Google email.</p><div ref={googleContainer} className="google-button"/></>:<p className="muted">Google linking will appear when the Google client ID is configured.</p>}<button className="primary" onClick={()=>void signOut()} disabled={authBusy}>Sign out <span>↗</span></button></>:<><h2>{authMode==='login'?'Welcome back, player.':'Create your player identity.'}</h2><div className="auth-tabs"><button className={authMode==='login'?'active':''} onClick={()=>{setAuthMode('login');setError('');}}>Sign in</button><button className={authMode==='register'?'active':''} onClick={()=>{setAuthMode('register');setError('');}}>Register</button></div><form className="auth-form" onSubmit={e=>void submitAuth(e)}><label>{authMode==='login'?'Username or email':'Username'}<input autoComplete={authMode==='login'?'username':'username'} required minLength={3} maxLength={254} value={identity} onChange={e=>setIdentity(e.target.value)} placeholder="Enter username or email"/></label>{authMode==='register'&&<label>Email address<input type="email" autoComplete="email" required maxLength={254} value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com"/></label>}<label>Password<input type="password" autoComplete={authMode==='login'?'current-password':'new-password'} required minLength={authMode==='register'?12:1} value={password} onChange={e=>setPassword(e.target.value)} placeholder={authMode==='register'?'At least 12 characters':'Your password'}/></label><button className="primary" disabled={authBusy||authBooting}>{authBooting?'Opening secure access…':authBusy?'Processing…':authMode==='login'?'Sign in':'Create account'} <span>↗</span></button></form>{system?.google_login_configured?<><p className="muted">Or use your Google account:</p><div className="google-button" ref={googleContainer}/></>:<p className="muted">Google sign-in is optional and can be enabled from the local configuration. Email/password accounts work without it.</p>}</>}{message&&<p role="status" className="feedback">{message}</p>}{error&&<p role="alert" className="auth-error">{error}</p>}</div></section>}
 {page==='Roadmap'&&<section className="panel roadmap">{phases.map((name,i)=><div className={'roadmap-row '+(i===3?'current':'')} key={name}><span className="phase-num">{String(i+1).padStart(2,'0')}</span><div><h3>{name}</h3><p>{i===0?'App shell, PostgreSQL configuration, diagnostics and Windows setup.':i===1?'Registration, Google sign-in option and separate local-only admin service.':i===2?'Private player preferences, goals and weekly availability.':i===3?'Reviewed exercises and plans matched to the user’s starting ability.':i===5?'Independent skill progression, recovery-aware quests and optional game penalties.':'Scheduled for a later integrated release.'}</p></div><span className="mini-tag">{i===0?'COMPLETED':i===1?'COMPLETED':i===2?'COMPLETED':i===3?'THIS RELEASE':'UPCOMING'}</span></div>)}</section>}
 {page==='System status'&&<><section className="panel"><div className="section-heading"><div><span className="eyebrow">LIVE DIAGNOSTICS</span><h2>Connection health</h2></div><button className="primary" onClick={()=>void check()} disabled={busy}>{busy?'Checking…':'Check again'} <span>↻</span></button></div><div className="health-grid"><div><span>React interface</span><strong className="green">Running</strong></div><div><span>Django API</span><strong>{health?'Online':'Unavailable'}</strong></div><div><span>PostgreSQL connection</span><strong className={online?'green':''}>{health?.database || 'Not checked'}</strong></div></div><p role="status" className="feedback">{error || (health?.database==='unavailable'?'API is running, but the database is unreachable. Check PostgreSQL.':online?'API and database responded successfully.':'Checking local services…')}</p><p className="muted">Google sign-in: {system?.google_login_configured?'configured':'not configured (email/password still works)'}. Local admin: http://127.0.0.1:8001/admin/ (only when separately started).</p></section><section className="panel secondary"><h2>Local first. Private by default.</h2><p>Public API and admin are separate. Both listen only on your PC. Mobile installation and public QR access arrive in Phase 9.</p><dl><dt>Frontend</dt><dd>127.0.0.1:5173</dd><dt>Backend</dt><dd>127.0.0.1:8000</dd><dt>Local admin</dt><dd>127.0.0.1:8001</dd><dt>Database</dt><dd>monarch_system</dd></dl></section></>}
 <footer><span>MONARCH SYSTEM</span><span>Built for real life. Designed for your next level.</span><span>CINEMATIC EDITION / v0.4.3</span></footer></main></div></div>;
}
