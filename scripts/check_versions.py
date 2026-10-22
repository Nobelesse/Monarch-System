import subprocess
import sys
if sys.version_info[:2] != (3, 12):
    raise SystemExit('Use Python 3.12: py -3.12 -m venv .venv')
node = subprocess.check_output(['node', '--version'], text=True).strip()
parts = tuple(map(int, node.lstrip('v').split('.')))
if parts[0] != 22 or parts < (22, 12, 0):
    raise SystemExit('This release targets Node 22.12+ within Node 22. Your version: '+node)
print('Python '+sys.version.split()[0]+' and Node '+node+' passed the release checks.')
