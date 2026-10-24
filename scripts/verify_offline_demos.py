"""Offline exercise coverage gate: keep renderer in sync with all Django catalog slugs."""
from __future__ import annotations
from pathlib import Path
import ast,re
ROOT=Path(__file__).resolve().parents[1]
MIGRATIONS=ROOT/'backend/core/migrations'
LIB=ROOT/'frontend/src/offline-exercises.ts'
RENDER=ROOT/'frontend/src/offline-human-renderer.ts'
GUIDE=ROOT/'frontend/src/OfflineHumanGuide.tsx'
WORKOUT=ROOT/'frontend/src/Workout.tsx'
slugs=set()
for name in ('0004_workout_engine.py','0005_workout_refinements.py'):
    program=ast.parse((MIGRATIONS/name).read_text(encoding='utf-8'))
    array=next(x.value for x in program.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CATALOG' for t in x.targets))
    values=ast.literal_eval(array)
    for row in values:
        if row[0] in slugs:raise AssertionError('duplicate exercise slug: '+row[0])
        slugs.add(row[0])
lib=LIB.read_text(encoding='utf-8')
keys=set(re.findall(r'^  "([a-z0-9-]+)":',lib,re.M))
assert slugs==keys,(sorted(slugs-keys),sorted(keys-slugs))
assert len(slugs)==63
poses=set(re.findall(r'"pose": "([a-z_]+)"',lib))
assert len(poses)>=30
renderer=RENDER.read_text(encoding='utf-8')
assert 'exerciseJoints' in renderer and 'paintHuman' in renderer
assert 'window.fetch' not in renderer and 'https://' not in renderer
source=GUIDE.read_text(encoding='utf-8')
assert 'OFFLINE_EXERCISES[slug]' in source and 'paintHuman' in source
assert 'https://www.youtube' not in source.lower() and '<iframe' not in source.lower()
workout=WORKOUT.read_text(encoding='utf-8')
assert 'OfflineHumanGuide' in workout and 'SetCoach' in workout
assert 'HumanFormGuide' not in workout and 'iframe' not in workout
print(f'Offline movement library OK: {len(slugs)} exact exercise slugs, {len(poses)} named motion presets, no online runtime media.')
