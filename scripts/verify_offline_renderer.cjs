/* Runtime smoke test of all 63 offline human-motion presets without a browser/server. */
const fs=require('fs');const path=require('path');const assert=require('assert');
let ts;try{ts=require(path.resolve(__dirname,'../frontend/node_modules/typescript'));}catch{ts=require('typescript');}
const root=path.resolve(__dirname,'../frontend/src');
function load(file){const src=fs.readFileSync(path.join(root,file),'utf8');const js=ts.transpileModule(src,{fileName:file,compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;const exp={};new Function('exports','module',js)(exp,{exports:exp});return exp;}
const {OFFLINE_EXERCISES}=load('offline-exercises.ts');const {exerciseJoints,paintHuman}=load('offline-human-renderer.ts');
const colors={addColorStop(){}};
const context={save(){},restore(){},closePath(){},createLinearGradient(){return colors;},createRadialGradient(){return colors;},fillRect(){},beginPath(){},ellipse(){},fill(){},stroke(){},moveTo(){},lineTo(){},fillText(){},strokeRect(){},arc(){}};
let n=0;
for(const e of Object.values(OFFLINE_EXERCISES)){
 assert(e.slug&&e.name&&e.instructions);n++;
 for(const phase of [0,.125,.25,.5,.75]){
  const j=exerciseJoints(e,phase);
  assert(Object.keys(j).length>=16);
  for(const v of Object.values(j))assert([v.x,v.y,v.z].every(Number.isFinite),`Invalid 3D joint for ${e.slug}`);
  for(const yaw of [-55,25,55])paintHuman(context,960,540,e,phase,yaw);
 }
}
assert.strictEqual(n,63);
console.log(`Offline 3D runtime smoke PASSED: ${n} exercises, 5 motion positions and 3 viewpoints per exercise.`);
