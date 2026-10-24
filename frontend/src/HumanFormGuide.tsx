/**
 * Human-first exercise demonstration player.
 * Deliberately DOES NOT synthesize or display a misleading generic mannequin motion.
 * Only exact-slug, locally supplied human recordings or rigged motion exports play.
 * No external media is uploaded or sent to Monarch servers.
 */
import {useEffect, useRef, useState} from 'react';
import seatedReference from './assets/trainer-seated.webp';
import './human-form-guide.css';

type Movement = 'squat'|'hinge'|'push'|'pull'|'core'|'mobility';
type Entry = {slug:string; filename:string; kind:'video'|'3d'; credit?:string; checked?:boolean};
type Manifest = {version:number; demos:Entry[]};
const motionHints:Record<Movement,{cue:string;avoid:string}>={
 squat:{cue:'Bend at the hips and knees through a comfortable range. Keep feet stable.',avoid:'Do not force painful knee ranges.'},
 hinge:{cue:'Move from your hips, gently shifting them backward before returning upright.',avoid:'Avoid forcing your lower back into a rounded position.'},
 push:{cue:'Keep your body stable as you push away, then return with control.',avoid:'Do not force a painful shoulder or wrist position.'},
 pull:{cue:'Move slowly, bringing elbows back without jerking the body.',avoid:'Avoid shrugging or swinging to complete the movement.'},
 core:{cue:'Breathe normally and use a small, controlled range.',avoid:'Stop if the movement causes back or hip pain.'},
 mobility:{cue:'Move slowly within a comfortable, pain-free range.',avoid:'Do not force a stretch or bounce through discomfort.'},
};
const FILE_NAME = /^[a-z0-9][a-z0-9_-]*\.(mp4|webm|glb)$/;
const SLUG = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
function cleanEntry(item:unknown):Entry|null{
 if(!item||typeof item!=='object')return null;
 const o=item as Record<string,unknown>;
 if(typeof o.slug!=='string'||!SLUG.test(o.slug)||typeof o.filename!=='string'||!FILE_NAME.test(o.filename))return null;
 const kind=o.filename.endsWith('.glb')?'3d':'video';
 if(o.kind!==kind)return null;
 return {slug:o.slug,filename:o.filename,kind,credit:typeof o.credit==='string'?o.credit.slice(0,160):undefined,checked:o.checked===true};
}
export async function getHumanDemo(slug:string):Promise<Entry|null>{
 if(!SLUG.test(slug))return null;
 const response=await fetch('/human-demos/manifest.json',{cache:'no-store'});
 if(!response.ok||!(response.headers.get('content-type')||'').includes('json'))return null;
 const body=await response.json() as Manifest;
 if(body.version!==1||!Array.isArray(body.demos))return null;
 return body.demos.map(cleanEntry).find((item):item is Entry=>item!==null&&item.slug===slug)??null;
}
const modelViewerUrl='https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js';
let modelScript:Promise<boolean>|undefined;
function prepareModelViewer():Promise<boolean>{
 if(typeof window==='undefined')return Promise.resolve(false);
 if(customElements.get('model-viewer'))return Promise.resolve(true);
 if(modelScript)return modelScript;
 modelScript=new Promise(resolve=>{
  const tag=document.createElement('script');tag.type='module';tag.src=modelViewerUrl;
  tag.onload=()=>resolve(Boolean(customElements.get('model-viewer')));
  tag.onerror=()=>resolve(false);
  document.head.append(tag);
 });
 return modelScript;
}
function useHumanDemo(slug:string){
 const [entry,setEntry]=useState<Entry|null>(null);
 const [loading,setLoading]=useState(true);
 useEffect(()=>{
  let active=true;setLoading(true);setEntry(null);
  void getHumanDemo(slug).then(d=>{if(active)setEntry(d);}).catch(()=>{if(active)setEntry(null);}).finally(()=>{if(active)setLoading(false);});
  return()=>{active=false;};
 },[slug]);
 return {entry,loading};
}
export default function HumanFormGuide({slug,name,movement,instructions}:{slug:string;name:string;movement:Movement;instructions:string}){
 const {entry,loading}=useHumanDemo(slug);
 const [tempUrl,setTempUrl]=useState<string|null>(null);
 const [tempName,setTempName]=useState('');
 const [playerError,setPlayerError]=useState(false);
 const [ready3D,setReady3D]=useState(false);
 const [playing,setPlaying]=useState(true);
 const [speed,setSpeed]=useState('1');
 const videoRef=useRef<HTMLVideoElement>(null);
 const uploadRef=useRef<HTMLInputElement>(null);
 const isSeated=/^seated knee raise$/i.test(name);
 const movie=Boolean(tempUrl||entry?.kind==='video');
 const isGLB=Boolean(!tempUrl&&entry?.kind==='3d');
 const videoSrc=tempUrl|| (entry?.kind==='video'?'/human-demos/media/'+entry.filename:null);
 const hints=motionHints[movement];
 useEffect(()=>{
  setPlayerError(false);setPlaying(true);
 },[slug,videoSrc]);
 useEffect(()=>{if(!isGLB){setReady3D(false);return;}let valid=true;void prepareModelViewer().then(ok=>{if(valid)setReady3D(ok);});return()=>{valid=false;};},[isGLB]);
 useEffect(()=>()=>{if(tempUrl)URL.revokeObjectURL(tempUrl);},[tempUrl]);
 const trainerSearch='https://www.youtube.com/results?search_query='+encodeURIComponent(name+' exercise proper form fitness trainer demonstration');
 function chooseFile(files:FileList|null){
  const file=files?.[0];if(!file)return;
  if(!['video/mp4','video/webm'].includes(file.type)||file.size>200*1024*1024){setPlayerError(true);return;}
  const next=URL.createObjectURL(file);setTempUrl(next);setTempName(file.name);setPlayerError(false);
 }
 return <section className="human-guide" aria-label={`Human exercise guide for ${name}`}>
  <header className="human-guide-top"><span>◈ FORM STUDIO / HUMAN COACH</span><strong>{name}</strong></header>
  <div className="human-guide-stage">
   {movie&&videoSrc&&!playerError?<div className="human-guide-video"><video key={videoSrc} ref={videoRef} src={videoSrc} controls playsInline preload="metadata" loop autoPlay={playing} muted onError={()=>setPlayerError(true)} aria-label={`Human instructor exercise demonstration for ${name}`}/><div className="human-guide-label">{tempUrl?'LOCAL VIDEO · PREVIEW ONLY':entry?.checked?'REVIEWED MEDIA':'USER-SUPPLIED MEDIA · VERIFY FORM'}</div></div>:null}
   {isGLB&&ready3D&&!playerError?<div className="human-guide-model">{<div ref={node=>{
      if(!node||node.childNodes.length)return;
      const el=document.createElement('model-viewer');
      el.setAttribute('src','/human-demos/media/'+entry!.filename);
      el.setAttribute('camera-controls','');el.setAttribute('autoplay','');el.setAttribute('animation-crossfade-duration','200');
      el.setAttribute('shadow-intensity','1');el.setAttribute('interaction-prompt','none');
      el.setAttribute('environment-image','neutral');
      el.setAttribute('aria-label',`Interactive human 3D form model for ${name}`);
      el.style.width='100%';el.style.height='330px';el.addEventListener('error',()=>setPlayerError(true));node.append(el);
     }}/>}<span>DRAG TO ROTATE · HUMAN 3D MOTION</span></div>:null}
   {(!movie&&!isGLB||playerError||isGLB&&!ready3D)&&<div className="human-guide-placeholder">
    {isSeated?<img src={seatedReference} alt="Adult trainer seated on a bench with knee raised — static pose reference"/>:<div className="human-guide-placeholder-art" aria-hidden="true"><span>◇</span><strong>HUMAN MOTION LIBRARY</strong></div>}
    <div className="human-guide-placeholder-copy"><span>{isSeated?'HUMAN POSITION REFERENCE':'EXACT DEMONSTRATION NOT INSTALLED'}</span><h4>{name}</h4><p>{isSeated?'This is a real-human styled static pose illustration, not an animated technique guide.':'The old mannequin is removed. No substitute generic animation is shown for this exercise because beginners need the correct movement.'}</p>{playerError&&<small role="alert">Could not load this media. Check the file format and asset path.</small>}</div>
   </div>}
  </div>
  <div className="human-guide-tools">
   {movie&&!playerError&&<label>Playback speed <select value={speed} onChange={e=>{setSpeed(e.target.value);if(videoRef.current)videoRef.current.playbackRate=Number(e.target.value);}}><option value="0.5">0.5×</option><option value="0.75">0.75×</option><option value="1">1×</option><option value="1.25">1.25×</option></select></label>}
   <button type="button" className="human-guide-upload" onClick={()=>uploadRef.current?.click()}>▣ Preview a human video</button>
   <input ref={uploadRef} type="file" accept="video/mp4,video/webm" hidden onChange={e=>{chooseFile(e.target.files);e.target.value='';}} aria-label="Choose a human exercise demonstration video"/>
   {tempUrl&&<button type="button" onClick={()=>{setTempUrl(null);setTempName('');}}>Clear local preview</button>}
   <a href={trainerSearch} target="_blank" rel="noopener noreferrer">Find human demonstration ↗</a>
  </div>
  {tempName&&<div className="human-guide-small">Viewing local clip: {tempName}. This stays in your browser and is not uploaded or permanently saved.</div>}
  {entry?.credit&&<div className="human-guide-small">Media credit: {entry.credit}</div>}
  {loading&&<div className="human-guide-small">Checking locally installed exercise demonstrations…</div>}
  <div className="human-guide-instructions"><div><small>EXERCISE-SPECIFIC INSTRUCTIONS</small><p>{instructions}</p></div><div><small>MOVEMENT CUE</small><p>{hints.cue}</p></div><div><small>BEFORE YOU COPY A DEMO</small><p>{hints.avoid} Check the exercise name and equipment match the video.</p></div></div>
  <p className="human-guide-disclaimer">For beginners: don't imitate a generic animation. Use only a demo of the exact exercise from a qualified instructor. Stop if you experience pain or dizziness. Human videos or motion-capture GLBs can be added locally; unreviewed footage is not presented as verified coaching.</p>
 </section>;
}
