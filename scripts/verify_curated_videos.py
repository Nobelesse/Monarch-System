"""Offline sanity checks for the exact-exercise human instructor index.
Not a claim of validating third-party video availability or technique.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
video_file = root / 'frontend/src/curated-human-videos.ts'
player_file = root / 'frontend/src/HumanFormGuide.tsx'
source = video_file.read_text(encoding='utf-8')
player = player_file.read_text(encoding='utf-8')
slugs: set[str] = set()
for path in sorted((root / 'backend/core/migrations').glob('000[45]*.py')):
    tree = ast.parse(path.read_text(encoding='utf-8'))
    for item in tree.body:
        if isinstance(item, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'CATALOG' for t in item.targets):
            slugs.update(entry[0] for entry in ast.literal_eval(item.value))
entries = re.findall(r"^  '([a-z0-9-]+)':\s*\{\s*videoId:\s*'([^']+)'", source, re.M)
assert len(entries) == 6, f'Expected six explicitly researched sources, got {len(entries)}'
assert len(set(x[0] for x in entries)) == len(entries), 'Duplicate exercise ID'
for slug, video_id in entries:
    assert slug in slugs, f'No matching catalog exercise for {slug}'
    assert re.fullmatch(r'[a-zA-Z0-9_-]{11}', video_id), f'Invalid YouTube video ID for {slug}'
assert 'getInstructorDemo(slug)' in player
assert 'youtube-nocookie.com/embed/' in player
assert 'Watch on YouTube' in player
assert 'entry&&instructor' in player, 'Local video must have priority over YouTube'
print(f'Curated exercise index OK: {len(entries)} real instructor links; all slugs exist in catalog.')
print('YouTube embed availability must be checked in Chrome with internet access.')
