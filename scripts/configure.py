"""Local setup. Never prints or places passwords in command history."""
import getpass
import json
import secrets
from pathlib import Path
root = Path(__file__).resolve().parent.parent
path = root / 'backend' / 'config.local.json'
if path.exists():
    print('Existing configuration preserved. Edit backend/config.local.json locally if credentials change.')
else:
    password = getpass.getpass('Enter the PostgreSQL password for monarch_app: ')
    if not password:
        raise SystemExit('Password cannot be empty. No file written.')
    confirm = getpass.getpass('Enter it again: ')
    if password != confirm:
        raise SystemExit('Passwords did not match. No file written.')
    with path.open('x', encoding='utf-8') as handle:
        json.dump({'secret_key': secrets.token_urlsafe(64), 'database_password': password}, handle, indent=2)
    print('Local configuration created. This file is excluded from Git. Do not share it.')
