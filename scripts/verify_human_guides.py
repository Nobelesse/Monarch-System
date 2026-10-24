"""Dependency-free static smoke audit of optional human motion assets."""
from pathlib import Path
import json
import re
import sys
ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'frontend' / 'public' / 'human-demos'
SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
FILENAME = re.compile(r'^[a-z0-9][a-z0-9_-]*\.(mp4|webm|glb)$')

def main() -> int:
    manifest = json.loads((PUBLIC/'manifest.json').read_text(encoding='utf-8-sig'))
    assert manifest['version'] == 1, 'Manifest schema version incorrect'
    assert isinstance(manifest['demos'], list), 'demos must be an array'
    seen: set[str] = set()
    for entry in manifest['demos']:
        slug, fn = entry['slug'], entry['filename']
        assert SLUG.fullmatch(slug) and FILENAME.fullmatch(fn), f'Unsafe media path: {slug}, {fn}'
        assert slug not in seen, f'Duplicate exercise slug: {slug}'
        seen.add(slug)
        expected = '3d' if fn.endswith('.glb') else 'video'
        assert entry['kind'] == expected, f'Media kind mismatch: {fn}'
        assert (PUBLIC/'media'/fn).is_file(), f'Missing media asset: {fn}'
    source = (ROOT/'frontend'/'src'/'Workout.tsx').read_text(encoding='utf-8')
    assert 'HumanFormGuide' in source, 'The new human guide has not been wired in'
    assert 'ExerciseMotion3D' not in source, 'Old mannequin should not be rendered'
    assert not (ROOT/'frontend'/'src'/'ExerciseMotion3D.tsx').exists(), 'Legacy mannequin component still exists'
    print(f'Human demo audit PASSED ({len(seen)} locally installed licensed media files).')
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except (AssertionError, KeyError, ValueError) as exc:
        print('Human demo audit FAILED:', exc)
        sys.exit(1)
