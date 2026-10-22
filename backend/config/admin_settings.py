"""Separate local-only admin service. Start via scripts/admin.ps1, never a tunnel."""
from .settings import *  # noqa: F401,F403
INSTALLED_APPS = ['django.contrib.admin', 'django.contrib.messages', 'django.contrib.staticfiles'] + INSTALLED_APPS
MIDDLEWARE = ['config.admin_guard.LoopbackOnlyMiddleware'] + MIDDLEWARE + ['django.contrib.messages.middleware.MessageMiddleware']
ROOT_URLCONF = 'config.admin_urls'
SESSION_COOKIE_NAME = 'monarch_admin_session'
CSRF_COOKIE_NAME = 'monarch_admin_csrf'

# The admin listener is intentionally not a target of the Vite proxy.
# Do not inherit the public app's CSRF-trusted frontend origins.
CSRF_TRUSTED_ORIGINS = []
