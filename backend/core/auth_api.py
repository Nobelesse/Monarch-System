"""Same-origin session authentication API; deliberately no JWT/localStorage tokens.

Django CSRF middleware protects every unsafe method, including anonymous login/register.
"""
import json
import re
import secrets
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.contrib.auth.validators import UnicodeUsernameValidator
from .models import PlayerPaths, SocialIdentity, PlayerProfile

ALLOWED_MODULES = {'workout', 'study', 'learning'}


def reply(message, status=400):
    return JsonResponse({'error': message}, status=status)


def payload(request):
    if int(request.META.get('CONTENT_LENGTH') or 0) > 8192 or len(request.body) > 8192:
        raise ValueError('Request is too large.')
    try:
        data = json.loads(request.body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError('Invalid JSON.') from exc
    if not isinstance(data, dict):
        raise ValueError('Expected an object.')
    return data


def valid_paths(values):
    if (not isinstance(values, list) or not (1 <= len(values) <= 3)
            or any(not isinstance(v, str) or v not in ALLOWED_MODULES for v in values)
            or len(set(values)) != len(values)):
        raise ValueError('Choose one or more distinct valid paths.')
    return values


def profile(user):
    paths, _ = PlayerPaths.objects.get_or_create(user=user)
    return {'id': user.pk, 'username': user.username, 'email': user.email,
            'modules': paths.modules, 'is_staff': user.is_staff}


@ensure_csrf_cookie
@require_GET
def csrf(request):
    return JsonResponse({'csrf': 'ready'})


@require_GET
def me(request):
    if not request.user.is_authenticated:
        return reply('Sign in to continue.', 401)
    return JsonResponse({'user': profile(request.user)})


@require_POST
def register(request):
    try:
        data = payload(request)
        username = data.get('username', '')
        email = data.get('email', '')
        password = data.get('password', '')
        modules = valid_paths(data.get('modules', ['workout']))
        if not isinstance(username, str) or not (3 <= len(username) <= 32) or '@' in username:
            return reply('Username must contain 3–32 characters and no @ symbol.')
        UnicodeUsernameValidator()(username)
        if not isinstance(email, str) or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email) or len(email) > 254:
            return reply('Enter a valid email address.')
        email = email.strip().lower()
        if not isinstance(password, str):
            return reply('Enter a password.')
        if get_user_model().objects.filter(username__iexact=username).exists() or get_user_model().objects.filter(email__iexact=email).exists():
            return reply('Username or email already registered.', 409)
        user = get_user_model()(username=username, email=email)
        validate_password(password, user=user)
        with transaction.atomic():
            user.set_password(password)
            user.save()
            PlayerPaths.objects.create(user=user, modules=modules)
    except (ValueError, ValidationError) as e:
        return reply('; '.join(e.messages) if isinstance(e, ValidationError) else str(e))
    except IntegrityError:
        return reply('Username or email already registered.', 409)
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return JsonResponse({'user': profile(user)}, status=201)


def rate_limit(request, identifier):
    # Lightweight local development throttle; use shared cache/proxy limits for deployment.
    import hashlib
    ip = request.META.get('REMOTE_ADDR', '')
    k = 'login-attempts:' + hashlib.sha256(f'{ip}:{identifier.lower()}'.encode()).hexdigest()
    count = cache.get(k, 0)
    return k, count >= 8


@require_POST
def sign_in(request):
    try:
        data = payload(request)
    except ValueError as e:
        return reply(str(e))
    identifier = data.get('identifier', '')
    password = data.get('password', '')
    if not isinstance(identifier, str) or not isinstance(password, str) or len(identifier) > 254:
        return reply('Invalid credentials.', 401)
    key, blocked = rate_limit(request, identifier)
    if blocked:
        return reply('Too many attempts. Try again later.', 429)
    User = get_user_model()
    user_match = (User.objects.filter(email__iexact=identifier).first() if '@' in identifier
                  else User.objects.filter(username__iexact=identifier).first())
    username = user_match.username if user_match else identifier
    user = authenticate(request, username=username, password=password)
    if user is None:
        cache.set(key, cache.get(key, 0) + 1, timeout=900)
        return reply('Invalid credentials.', 401)
    cache.delete(key)
    login(request, user)
    return JsonResponse({'user': profile(user)})


@require_POST
def sign_out(request):
    if not request.user.is_authenticated:
        return reply('Sign in to continue.', 401)
    logout(request)
    return JsonResponse({'signed_out': True})


@require_http_methods(['GET', 'PUT'])
def paths(request):
    if not request.user.is_authenticated:
        return reply('Sign in to continue.', 401)
    if request.method == 'GET':
        return JsonResponse({'modules': profile(request.user)['modules']})
    try:
        modules = valid_paths(payload(request).get('modules'))
    except ValueError as e:
        return reply(str(e))
    own, _ = PlayerPaths.objects.get_or_create(user=request.user)
    if own.modules != modules:
        PlayerProfile.objects.filter(user=request.user).update(completed_at=None, current_step=2)
    own.modules = modules
    own.save(update_fields=['modules', 'updated_at'])
    return JsonResponse({'modules': own.modules})


def verify_google(credential):
    """Verify Google's signed ID token (signature, issuer, expiration, audience)."""
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token
    return id_token.verify_oauth2_token(credential, google_requests.Request(), settings.GOOGLE_CLIENT_ID)


def google_claims(request):
    if not settings.GOOGLE_CLIENT_ID:
        raise ValueError('Google sign-in is not configured on this installation.')
    data = payload(request)
    credential = data.get('credential', '')
    if not isinstance(credential, str) or not (100 <= len(credential) <= 10000):
        raise ValueError('Invalid Google credential.')
    try:
        claims = verify_google(credential)
    except Exception as exc:
        # Never reveal Google token, certificate or provider response details.
        raise ValueError('Google verification failed.') from exc
    if (claims.get('iss') not in ('accounts.google.com', 'https://accounts.google.com')
            or claims.get('email_verified') not in (True, 'true')
            or not claims.get('sub') or not claims.get('email')):
        raise ValueError('Google account identity could not be verified.')
    return claims


@require_POST
def google_sign_in(request):
    try:
        claims = google_claims(request)
    except ValueError as e:
        return reply(str(e), 400)
    subject = str(claims['sub'])
    email = str(claims['email']).strip().lower()
    identity = SocialIdentity.objects.select_related('user').filter(provider='google', subject=subject).first()
    if identity:
        user = identity.user
        if not user.is_active:
            return reply('Account unavailable.', 403)
    else:
        # NEVER silently link a Google identity to an existing password account by email.
        if get_user_model().objects.filter(email__iexact=email).exists():
            return reply('An account with this email exists. Sign in with your password and link Google from your account.', 409)
        try:
            with transaction.atomic():
                username = 'google_' + secrets.token_hex(10)
                user = get_user_model()(username=username, email=email)
                user.set_unusable_password()
                user.save()
                PlayerPaths.objects.create(user=user)
                SocialIdentity.objects.create(user=user, provider='google', subject=subject)
        except IntegrityError:
            return reply('Account creation conflict. Try again.', 409)
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return JsonResponse({'user': profile(user)})


@require_POST
def google_link(request):
    if not request.user.is_authenticated:
        return reply('Sign in to continue.', 401)
    try:
        claims = google_claims(request)
    except ValueError as e:
        return reply(str(e), 400)
    if claims['email'].lower() != request.user.email.lower():
        return reply('Use the Google account with the same verified email address.', 403)
    if SocialIdentity.objects.filter(user=request.user, provider='google').exists():
        return reply('Google is already linked to this account.', 409)
    try:
        SocialIdentity.objects.create(user=request.user, provider='google', subject=str(claims['sub']))
    except IntegrityError:
        return reply('This Google account is linked to another user.', 409)
    return JsonResponse({'linked': True})
