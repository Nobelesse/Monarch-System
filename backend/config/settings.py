import json
import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
BASE_DIR = Path(__file__).resolve().parent.parent
TESTING = os.environ.get('MONARCH_TEST_MODE') == '1'
path = BASE_DIR / 'config.local.json'
if path.exists():
    LOCAL = json.loads(path.read_text(encoding='utf-8'))
elif TESTING:
    LOCAL = {'secret_key': 'test-only-not-for-deployment', 'database_password': ''}
else:
    raise ImproperlyConfigured('Run scripts/configure.py first to create backend/config.local.json.')
SECRET_KEY = LOCAL['secret_key']
DEBUG = False
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '[::1]']
# Vite runs on port 5173 and proxies /api/ to Django on port 8000.
# Browsers still send the Vite page's Origin header on POST/PUT. Explicitly
# allow only those local development origins; all other origins remain blocked.
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:5173', 'http://localhost:5173']
INSTALLED_APPS = ['django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'rest_framework', 'core']
MIDDLEWARE = ['config.private_api_cache.PrivateAPICacheMiddleware', 'django.middleware.security.SecurityMiddleware', 'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.common.CommonMiddleware', 'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware', 'django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'core.User'
AUTH_PASSWORD_VALIDATORS = [
 {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
 {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
 {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
 {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql', 'NAME': 'monarch_system', 'USER': 'monarch_app', 'PASSWORD': LOCAL['database_password'], 'HOST': '127.0.0.1', 'PORT': '5432', 'CONN_MAX_AGE': 0, 'OPTIONS': {'connect_timeout': 5}}}
if TESTING:
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
REST_FRAMEWORK = {'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'], 'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer']}
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True

# Phase 2: browser-based session auth and optional Google Identity Services.
GOOGLE_CLIENT_ID = os.environ.get('MONARCH_GOOGLE_CLIENT_ID', LOCAL.get('google_client_id', '')).strip()
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [],
              'APP_DIRS': True, 'OPTIONS': {'context_processors': [
                  'django.template.context_processors.request',
                  'django.contrib.auth.context_processors.auth',
                  'django.contrib.messages.context_processors.messages',
              ]}}]
STATIC_URL = '/static/'
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                      'LOCATION': 'monarch-local-auth-throttle'}}
SESSION_COOKIE_AGE = 604800
SESSION_COOKIE_NAME = 'monarch_session'
# This build runs on 127.0.0.1 over HTTP. Use Secure cookies when deploying HTTPS.

# Phase 4.2: never use a persistent browser session after closing Chrome.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
