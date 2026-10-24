"""Build a static catalogue of exact-slug, offline illustrative 3D movement presets.
No downloaded video, external CDN, or online runtime dependency.
"""
from pathlib import Path
import ast, json
root=Path(__file__).resolve().parents[1]
entries=[]
for fn in ['0004_workout_engine.py','0005_workout_refinements.py']:
    tree=ast.parse((root/'backend/core/migrations'/fn).read_text(encoding='utf-8'))
    node=next(a for a in tree.body if isinstance(a,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CATALOG' for t in a.targets))
    entries.extend(ast.literal_eval(node.value))
# Each slug explicitly maps to motion category, pose and equipment; no silent family fallback.
groups={
 'sit_stand':'chair-sit-to-stand box-squat',
 'squat':'supported-shallow-squat goblet-squat band-squat gym-hack-squat',
 'leg_press':'gym-leg-press',
 'lunge':'reverse-lunge-supported dumbbell-split-squat',
 'step_up':'step-up-low',
 'hinge':'standing-hip-hinge dumbbell-romanian-deadlift kettlebell-deadlift good-morning-bodyweight band-pull-through kettlebell-suitcase-deadlift',
 'single_hinge':'single-leg-hinge-supported',
 'back_extension':'gym-back-extension',
 'bridge':'glute-bridge dumbbell-glute-bridge',
 'incline_push':'wall-pushup incline-pushup counter-pushup',
 'floor_push':'floor-pushup',
 'bench_press':'dumbbell-floor-press dumbbell-chest-press kettlebell-floor-press',
 'seated_press':'seated-chest-press band-chest-press',
 'overhead_press':'dumbbell-shoulder-press',
 'pec_fly':'gym-pec-deck',
 'scapular':'shoulder-blade-squeeze',
 'prone_raise':'prone-w-raise',
 'row':'band-row dumbbell-row seated-cable-row kettlebell-supported-row chest-supported-row',
 'band_apart':'band-pull-apart',
 'towel_hold':'towel-isometric-row',
 'lat_pulldown':'gym-lat-pulldown',
 'brace':'standing-brace',
 'dead_bug':'dead-bug',
 'bird_dog':'bird-dog',
 'side_plank':'side-plank-knees',
 'pallof':'pallof-press gym-cable-pallof',
 'carry':'suitcase-carry kettlebell-farmer-hold',
 'knee_lift':'standing-knee-lift gentle-march',
 'seated_march':'seated-knee-raise seated-hip-march',
 'calf_raise':'standing-calf-mobility',
 'calf_stretch':'wall-calf-stretch',
 'shoulder_circles':'seated-shoulder-circles',
 'side_reach':'standing-side-reach',
 'torso_rotation':'seated-thoracic-rotation',
 'ankle_circles':'ankle-circles',
 'neck_turns':'neck-range-check',
 'wrist_circles':'wrist-flexion-release',
 'hip_circles':'standing-hip-circle',
 'band_mobility':'band-shoulder-mobility',
}
map_slug={}
for pose,chunk in groups.items():
 for slug in chunk.split():
  if slug in map_slug: raise ValueError('duplicate mapping '+slug)
  map_slug[slug]=pose
all_slugs=[entry[0] for entry in entries]
missing=set(all_slugs)-set(map_slug); extra=set(map_slug)-set(all_slugs)
if missing or extra: raise ValueError(f'missing {missing} extra {extra}')
# A few differentiated environmental anchors for a specific exercise
supports={'chair-sit-to-stand':'chair','box-squat':'bench','gym-leg-press':'machine','seated-chest-press':'machine','seated-cable-row':'machine','seated-knee-raise':'bench','seated-hip-march':'bench','ankle-circles':'bench','seated-shoulder-circles':'bench','seated-thoracic-rotation':'bench','dumbbell-shoulder-press':'bench','wall-pushup':'wall','counter-pushup':'counter','incline-pushup':'bench','step-up-low':'step','gym-pec-deck':'machine','gym-lat-pulldown':'machine','gym-hack-squat':'machine','gym-back-extension':'bench','chest-supported-row':'bench','dumbbell-chest-press':'bench'}
for e in entries:
 slug,name,movement,equipment,level,caution,instructions=e
 if equipment in ('dumbbells','kettlebell','resistance_bands') and slug not in supports:supports[slug]=equipment
# Render all 63 exercise names and guidance: separate from workout prescription
out=['/* Generated from Django migrations. Do not use unlisted generic movement. */',"export type DemoPose = '"+"' | '".join(groups)+"';",'export type OfflineExercise = {slug:string;name:string;pose:DemoPose;movement:string;equipment:string;support:string;instructions:string};','export const OFFLINE_EXERCISES: Record<string, OfflineExercise> = {']
for slug,name,movement,equipment,level,caution,instructions in entries:
 item=dict(slug=slug,name=name,pose=map_slug[slug],movement=movement,equipment=equipment,support=supports.get(slug,'none'),instructions=instructions)
 out.append(f'  {json.dumps(slug)}: {json.dumps(item,ensure_ascii=False)},')
out.append('};')
out.append(f'export const OFFLINE_EXERCISE_COUNT = {len(entries)};')
(root/'frontend/src/offline-exercises.ts').write_text('\n'.join(out)+'\n',encoding='utf-8')
print(f'Wrote {len(entries)} explicit offline exercise specifications across {len(groups)} pose types')
