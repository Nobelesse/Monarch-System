"""Phase 3: account-scoped, atomic and resumable onboarding API.

No user ID is accepted from clients. Drafts can be partial; completion is validated.
No physiques are exposed outside the signed-in owner's onboarding endpoint.
"""
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .auth_api import payload, reply, ALLOWED_MODULES
from .models import (ModulePreference, PlayerPaths, PlayerProfile,
                     PrivatePhysique, WeeklyAvailability)

EXPERIENCE = {'beginner', 'intermediate', 'advanced'}
EQUIPMENT = {'bodyweight', 'dumbbells', 'resistance_bands', 'gym', 'kettlebell', 'other'}
LANGUAGES = {'en', 'hi'}


def validate_string(value, label, max_length, required=False):
    if not isinstance(value, str):
        raise ValueError(f'{label} must be text.')
    value = value.strip()
    if len(value) > max_length or (required and not value):
        raise ValueError(f'{label} must be {"1–" if required else "at most "}{max_length} characters.')
    if any(ord(c) < 32 for c in value):
        raise ValueError(f'{label} contains invalid characters.')
    return value


def validate_list(values, label, max_count, max_len):
    if not isinstance(values, list) or len(values) > max_count:
        raise ValueError(f'{label} must contain up to {max_count} entries.')
    cleaned = [validate_string(s, label, max_len, required=True) for s in values]
    if len(set(x.casefold() for x in cleaned)) != len(cleaned):
        raise ValueError(f'{label} contains duplicates.')
    return cleaned


def number_or_none(value, label, low, high):
    if value is None or value == '':
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(f'{label} must be a number or blank.')
    try:
        decimal = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f'{label} must be a number.') from exc
    if not decimal.is_finite() or not (Decimal(str(low)) <= decimal <= Decimal(str(high))):
        raise ValueError(f'{label} must be between {low} and {high}.')
    if decimal.as_tuple().exponent < -1:
        raise ValueError(f'{label} allows one decimal place.')
    return decimal


def snapshot(user):
    """Materialize an empty draft only for this authorized account."""
    profile, _ = PlayerProfile.objects.get_or_create(user=user)
    paths, _ = PlayerPaths.objects.get_or_create(user=user)
    selected = [x for x in paths.modules if x in ALLOWED_MODULES]
    by_module = {p.module: p for p in ModulePreference.objects.filter(user=user, module__in=selected)}
    preferences = {m: {
        'goal': by_module[m].goal if m in by_module else '',
        'experience': by_module[m].experience if m in by_module else 'beginner',
        'equipment': by_module[m].equipment if m in by_module else [],
        'topics': by_module[m].topics if m in by_module else [],
    } for m in selected}
    weekly = [{'module': x.module, 'weekday': x.weekday, 'minutes': x.minutes}
              for x in WeeklyAvailability.objects.filter(user=user, module__in=selected).order_by('module', 'weekday')]
    private = PrivatePhysique.objects.filter(user=user).first()
    physique = {
        'height_cm': float(private.height_cm) if 'workout' in selected and private and private.height_cm is not None else None,
        'weight_kg': float(private.weight_kg) if 'workout' in selected and private and private.weight_kg is not None else None,
    }
    return {'onboarding': {
        'display_name': profile.display_name or user.username,
        'timezone': profile.timezone,
        'language': profile.language,
        'reduced_motion': profile.reduced_motion,
        'high_contrast': profile.high_contrast,
        'current_step': profile.current_step,
        'completed': profile.completed_at is not None,
        'preferences': preferences,
        'schedule': weekly,
        'physique': physique,
    }, 'modules': selected}


def validated(data, modules):
    # Reject unknown fields rather than accidentally ignoring client ownership metadata.
    keys = {'display_name', 'timezone', 'language', 'reduced_motion', 'high_contrast',
            'current_step', 'completed', 'preferences', 'schedule', 'physique'}
    if set(data) != keys:
        raise ValueError('Invalid onboarding fields. Reload the page and try again.')
    name = validate_string(data['display_name'], 'Display name', 48, required=True)
    tz = validate_string(data['timezone'], 'Timezone', 64, required=True)
    try:
        ZoneInfo(tz)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError('Choose a valid IANA timezone (for example Asia/Kolkata).') from exc
    language = data['language']
    if not isinstance(language, str) or language not in LANGUAGES:
        raise ValueError('Unsupported language preference.')
    for key in ('reduced_motion', 'high_contrast', 'completed'):
        if not isinstance(data[key], bool):
            raise ValueError(f'{key} must be true or false.')
    step = data['current_step']
    if type(step) is not int or not (1 <= step <= 5):
        raise ValueError('Invalid onboarding step.')
    prefs = data['preferences']
    if not isinstance(prefs, dict) or set(prefs) != set(modules):
        raise ValueError('Preferences must match your selected paths. Reload the page.')
    clean_prefs = {}
    for module, row in prefs.items():
        if not isinstance(row, dict) or set(row) != {'goal', 'experience', 'equipment', 'topics'}:
            raise ValueError('Invalid module preference fields.')
        goal = validate_string(row['goal'], 'Goal', 160, required=data['completed'])
        level = row['experience']
        if not isinstance(level, str) or level not in EXPERIENCE:
            raise ValueError('Choose a valid experience level.')
        equipment = validate_list(row['equipment'], 'Equipment', 6, 30)
        topics = validate_list(row['topics'], 'Topics', 6, 48)
        if module != 'workout' and equipment:
            raise ValueError('Equipment belongs to the workout path only.')
        if module == 'workout' and any(x not in EQUIPMENT for x in equipment):
            raise ValueError('Choose valid workout equipment.')
        if module == 'workout' and topics:
            raise ValueError('Study or learning topics cannot be saved in workout.')
        clean_prefs[module] = {'goal': goal, 'experience': level, 'equipment': equipment, 'topics': topics}
    schedule = data['schedule']
    if not isinstance(schedule, list) or len(schedule) > 21:
        raise ValueError('Weekly schedule must contain at most 21 entries.')
    seen = set()
    clean_schedule = []
    for slot in schedule:
        if not isinstance(slot, dict) or set(slot) != {'module', 'weekday', 'minutes'}:
            raise ValueError('Invalid schedule entry.')
        module, weekday, minutes = slot['module'], slot['weekday'], slot['minutes']
        if not isinstance(module, str) or module not in modules:
            raise ValueError('Schedule contains an unselected path.')
        if type(weekday) is not int or not (0 <= weekday <= 6):
            raise ValueError('Weekdays must be Monday (0) through Sunday (6).')
        if type(minutes) is not int or not (15 <= minutes <= 240) or minutes % 15:
            raise ValueError('Each session must be 15–240 minutes, in 15-minute increments.')
        if (module, weekday) in seen:
            raise ValueError('Only one schedule entry per day and path is allowed.')
        seen.add((module, weekday))
        clean_schedule.append((module, weekday, minutes))
    if data['completed'] and any(not any(row[0] == m for row in clean_schedule) for m in modules):
        raise ValueError('Schedule at least one weekly session for each selected path.')
    physique = data['physique']
    if not isinstance(physique, dict) or set(physique) != {'height_cm', 'weight_kg'}:
        raise ValueError('Invalid optional physique fields.')
    height = number_or_none(physique['height_cm'], 'Height (cm)', 80, 250)
    weight = number_or_none(physique['weight_kg'], 'Weight (kg)', 20, 350)
    if 'workout' not in modules and (height is not None or weight is not None):
        raise ValueError('Optional physique fields require the workout path.')
    return {'display_name': name, 'timezone': tz, 'language': language,
            'reduced_motion': data['reduced_motion'], 'high_contrast': data['high_contrast'],
            'current_step': 5 if data['completed'] else step,
            'completed': data['completed'], 'preferences': clean_prefs,
            'schedule': clean_schedule, 'height_cm': height, 'weight_kg': weight}


@require_http_methods(['GET', 'PUT'])
def onboarding(request):
    if not request.user.is_authenticated:
        return reply('Sign in to continue.', 401)
    if request.method == 'GET':
        return JsonResponse(snapshot(request.user))
    try:
        # Request fields have no owner ID; ownership always comes from the session.
        data = payload(request)
        with transaction.atomic():
            paths, _ = PlayerPaths.objects.select_for_update().get_or_create(user=request.user)
            modules = paths.modules
            clean = validated(data, modules)
            profile, _ = PlayerProfile.objects.select_for_update().get_or_create(user=request.user)
            profile.display_name = clean['display_name']
            profile.timezone = clean['timezone']
            profile.language = clean['language']
            profile.reduced_motion = clean['reduced_motion']
            profile.high_contrast = clean['high_contrast']
            profile.current_step = clean['current_step']
            # Draft edits intentionally reopen completion until revalidated.
            if not clean['completed']:
                profile.completed_at = None
            elif profile.completed_at is None:
                profile.completed_at = timezone.now()
            profile.save()
            for module, row in clean['preferences'].items():
                ModulePreference.objects.update_or_create(user=request.user, module=module, defaults=row)
            # Preserve preferences of currently disabled modules so re-selection can restore goals.
            WeeklyAvailability.objects.filter(user=request.user).delete()
            WeeklyAvailability.objects.bulk_create([
                WeeklyAvailability(user=request.user, module=m, weekday=day, minutes=minutes)
                for m, day, minutes in clean['schedule']])
            if clean['height_cm'] is not None or clean['weight_kg'] is not None:
                PrivatePhysique.objects.update_or_create(user=request.user, defaults={
                    'height_cm': clean['height_cm'], 'weight_kg': clean['weight_kg']})
            else:
                PrivatePhysique.objects.filter(user=request.user).delete()
        return JsonResponse(snapshot(request.user))
    except ValueError as exc:
        return reply(str(exc))
