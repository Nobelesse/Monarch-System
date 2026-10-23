"""Phase 4: conservative, deterministic exercise drafts and same-pattern substitutions.

This is not health screening or a personalized medical prescription. No auto-logging,
XP, completed sessions or externally hosted exercise content are used here.
"""
import hashlib
import json
from django.db import transaction
from django.db.models import Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from .auth_api import payload, reply
from .models import (PlayerPaths, PlayerProfile, ModulePreference, WeeklyAvailability,
                     WorkoutExercise, WorkoutPlan, WorkoutSession, WorkoutPlanItem)
from .workout_catalog import CAUTION_TAGS, LEVELS, CATALOG_VERSION

DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
STRENGTH_MOVEMENTS = ('squat', 'hinge', 'push', 'pull', 'core')
FOCUS_MODES = ('balanced', 'strength', 'endurance', 'mobility')
PACES = ('easy', 'standard')
REP_OPTIONS = ('6–8 controlled', '6–10 controlled', '8–12 controlled', '10–15 controlled', '6–8 slow', '30 sec gently', '10–20 sec gently')
REST_OPTIONS = (30, 45, 60, 75, 90, 120)


def access(request):
    if not request.user.is_authenticated:
        return reply('Sign in to view Workout.', 401)
    paths = PlayerPaths.objects.filter(user=request.user).first()
    if not paths or 'workout' not in paths.modules:
        return reply('Select Workout under Your paths to use this feature.', 403)
    return None


def readiness(user):
    profile = PlayerProfile.objects.filter(user=user).first()
    pref = ModulePreference.objects.filter(user=user, module='workout').first()
    days = list(WeeklyAvailability.objects.filter(user=user, module='workout').order_by('weekday'))
    if not profile or not profile.completed_at:
        raise ValueError('Complete onboarding before generating a workout draft.')
    if not pref or not pref.goal.strip() or pref.experience not in LEVELS:
        raise ValueError('Set a Workout goal and experience level in Onboarding.')
    if not days:
        raise ValueError('Select at least one Workout day in Onboarding.')
    for day in days:
        if day.weekday > 6 or day.minutes < 15 or day.minutes > 240 or day.minutes % 15:
            raise ValueError('Onboarding contains invalid Workout availability. Update your schedule.')
    return pref, days


def equipment_for(preference):
    return set(preference.equipment) | {'bodyweight'}


def signature(preference, days, avoid, focus_mode="balanced", pace="standard"):
    state = {
        'catalog_version': CATALOG_VERSION, 'goal': preference.goal,
        'experience': preference.experience, 'equipment': sorted(equipment_for(preference)),
        'schedule': [(d.weekday, d.minutes) for d in days], 'avoid_tags': sorted(avoid),
        'focus_mode': focus_mode, 'pace': pace,
    }
    return hashlib.sha256(json.dumps(state, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def valid_exercises(preference, avoided):
    level = LEVELS.index(preference.experience)
    equipment = equipment_for(preference)
    return [e for e in WorkoutExercise.objects.filter(active=True)
            if e.equipment in equipment and e.minimum_level in LEVELS
            and LEVELS.index(e.minimum_level) <= level
            and isinstance(e.caution_tags, list)
            and not (set(e.caution_tags) & set(avoided))]


def to_exercise(e):
    return {'slug': e.slug, 'name': e.name, 'movement': e.movement,
            'equipment': e.equipment, 'level': e.minimum_level,
            'caution_tags': e.caution_tags, 'instructions': e.instructions}


def to_plan(plan, stale=False):
    sessions = WorkoutSession.objects.filter(plan=plan).prefetch_related(
        Prefetch('items', queryset=WorkoutPlanItem.objects.select_related('exercise').order_by('position'))
    ).order_by('weekday')
    return {
        'id': plan.pk, 'generated_at': plan.generated_at.isoformat(),
        'goal': plan.goal_snapshot, 'experience': plan.experience_snapshot,
        'equipment': plan.equipment_snapshot, 'avoid_tags': plan.avoid_tags,
        'focus_mode': plan.focus_mode, 'pace': plan.pace, 'stale': stale,
        'days': [{'weekday': s.weekday, 'day_name': DAY_NAMES[s.weekday],
                  'available_minutes': s.available_minutes, 'planned_minutes': s.planned_minutes,
                  'focus': s.focus, 'theme': s.theme, 'items': [
                      {'id': item.pk, 'position': item.position, 'sets': item.sets,
                       'reps': item.reps, 'rest_seconds': item.rest_seconds,
                       'exercise': to_exercise(item.exercise)} for item in s.items.all()
                  ]} for s in sessions],
    }


def is_stale(user, plan):
    try:
        pref, days = readiness(user)
    except ValueError:
        return True
    return plan.source_signature != signature(pref, days, plan.avoid_tags, plan.focus_mode, plan.pace)


def pick_strength_days(weekdays):
    """No adjacent strength days on the circular week; max three strength days."""
    chosen = []
    for day in sorted(weekdays):
        if len(chosen) >= 3:
            break
        if all((day - previous) % 7 not in (1, 6) for previous in chosen):
            chosen.append(day)
    return set(chosen)


def prescribe(exercise, experience, mobility=False):
    if mobility:
        return (1, '30 sec gently' if exercise.movement == 'mobility' else '6–8 slow', 30)
    if exercise.slug in ('standing-brace', 'side-plank-knees'):
        return (2 if experience == 'beginner' else 3, '10–20 sec gently', 60)
    return (2 if experience == 'beginner' else 3, '6–10 controlled', 75 if experience == 'beginner' else 90)


def choose_for_day(eligible, focus, weekday, count, theme='full_body', focus_mode='balanced'):
    if focus == 'mobility':
        pool = [e for e in eligible if e.movement == 'mobility']
        if not pool:
            raise ValueError('Your movement restrictions exclude all recovery activities. Review your exclusions.')
        return [pool[(weekday + n) % len(pool)] for n in range(min(count, len(pool)))]
    preferred = {
        'upper': ('push', 'pull', 'core', 'push', 'pull'),
        'lower': ('squat', 'hinge', 'core', 'squat', 'hinge'),
        'full_body': ('squat', 'hinge', 'push', 'pull', 'core'),
    }[theme]
    if focus_mode == 'strength' and theme == 'full_body':
        preferred = ('hinge', 'squat', 'push', 'pull', 'core')
    selected = []
    for pattern in preferred:
        options = [e for e in eligible if e.movement == pattern and e.pk not in {v.pk for v in selected}]
        if options:
            selected.append(options[(weekday + len(selected)) % len(options)])
        if len(selected) >= count:
            break
    if not selected:
        raise ValueError('No suitable strength exercises remain after exclusions. Adjust restrictions or equipment.')
    return selected


def training_theme(index, total):
    if total == 1:
        return 'full_body'
    if total == 2:
        return ('upper', 'lower')[index]
    return ('upper', 'lower', 'full_body')[index]


def safe_prescription(exercise, level, recovery, focus_mode, pace):
    sets, reps, rest = prescribe(exercise, level, recovery)
    if not recovery:
        if focus_mode == 'strength' and pace == 'standard':
            sets = min(4, sets + 1)
        elif focus_mode == 'endurance':
            reps = '10–15 controlled'
            rest = 60
        elif focus_mode == 'mobility':
            sets = min(2, sets)
        if pace == 'easy':
            sets = min(sets, 2)
            rest = max(rest, 75)
    return sets, reps, rest


@require_GET
def library(request):
    denied = access(request)
    if denied is not None:
        return denied
    return JsonResponse({'exercises': [to_exercise(e) for e in WorkoutExercise.objects.filter(active=True)],
                         'caution_tags': list(CAUTION_TAGS), 'catalog_version': CATALOG_VERSION})


@require_GET
def current_plan(request):
    denied = access(request)
    if denied is not None:
        return denied
    plan = WorkoutPlan.objects.filter(user=request.user).first()
    return JsonResponse({'plan': to_plan(plan, is_stale(request.user, plan)) if plan else None,
                         'limitations': 'Draft only. Not medical advice or health clearance. Stop for pain; consult a qualified professional about injuries.'})


@require_POST
def generate_plan(request):
    denied = access(request)
    if denied is not None:
        return denied
    try:
        data = payload(request)
        if not {'avoid_tags', 'acknowledged', 'regenerate'} <= set(data) or not set(data) <= {'avoid_tags', 'acknowledged', 'regenerate', 'focus_mode', 'pace'}:
            raise ValueError('Invalid generator fields. Reload Workout and retry.')
        focus_mode = data.get('focus_mode', 'balanced')
        pace = data.get('pace', 'standard')
        if not isinstance(focus_mode, str) or focus_mode not in FOCUS_MODES:
            raise ValueError('Choose a supported training focus.')
        if not isinstance(pace, str) or pace not in PACES:
            raise ValueError('Choose a supported intensity preference.')
        avoided = data['avoid_tags']
        if (not isinstance(avoided, list) or len(avoided) > len(CAUTION_TAGS)
                or any(not isinstance(x, str) or x not in CAUTION_TAGS for x in avoided)
                or len(set(avoided)) != len(avoided)):
            raise ValueError('Select only supported movement exclusions without duplicates.')
        if data['acknowledged'] is not True or type(data['regenerate']) is not bool:
            raise ValueError('Please acknowledge the draft limitations; regenerate must be true or false.')
        with transaction.atomic():
            # Serialize generation for this owner, avoiding concurrent duplicate drafts.
            PlayerPaths.objects.select_for_update().get(user=request.user)
            preference, days = readiness(request.user)
            token = signature(preference, days, avoided, focus_mode, pace)
            current = WorkoutPlan.objects.filter(user=request.user).first()
            if current and current.source_signature == token and not data['regenerate']:
                return JsonResponse({'plan': to_plan(current), 'reused': True})
            eligible = valid_exercises(preference, avoided)
            strength = pick_strength_days([d.weekday for d in days])
            if focus_mode in ('endurance','mobility') and len(strength) > 2:
                strength = set(sorted(strength)[:2])
            strength_order = sorted(strength)
            # Construct the whole plan in memory BEFORE modifying existing draft.
            draft = []
            for day in days:
                focus = 'strength' if day.weekday in strength else 'mobility'
                cap = (60 if preference.experience == 'beginner' else 75 if preference.experience == 'intermediate' else 90)
                minutes = min(day.minutes, cap if focus == 'strength' else 30)
                if pace == 'easy':
                    minutes = min(minutes, 40 if focus == 'strength' else 20)
                count = max(1, min((4 if pace == 'easy' else 5) if focus == 'strength' else 3, (minutes - 6) // 12 + 1))
                theme = training_theme(strength_order.index(day.weekday), len(strength_order)) if focus == 'strength' else 'recovery'
                exercises = choose_for_day(eligible, focus, day.weekday, count, theme, focus_mode)
                draft.append((day.weekday, day.minutes, minutes, focus, theme, exercises))
            if current:
                current.days.all().delete()
                plan = current
                plan.source_signature = token
                plan.goal_snapshot = preference.goal
                plan.experience_snapshot = preference.experience
                plan.equipment_snapshot = sorted(equipment_for(preference))
                plan.avoid_tags = sorted(avoided)
                plan.focus_mode = focus_mode
                plan.pace = pace
                plan.save()
            else:
                plan = WorkoutPlan.objects.create(
                    user=request.user, source_signature=token, goal_snapshot=preference.goal,
                    experience_snapshot=preference.experience, equipment_snapshot=sorted(equipment_for(preference)),
                    avoid_tags=sorted(avoided), focus_mode=focus_mode, pace=pace)
            for day, available, planned, focus, theme, exercises in draft:
                session = WorkoutSession.objects.create(plan=plan, weekday=day,
                    available_minutes=available, planned_minutes=planned, focus=focus, theme=theme)
                for index, exercise in enumerate(exercises, 1):
                    sets, reps, rest = safe_prescription(exercise, preference.experience, focus == 'mobility', focus_mode, pace)
                    WorkoutPlanItem.objects.create(session=session, exercise=exercise,
                        position=index, sets=sets, reps=reps, rest_seconds=rest)
        return JsonResponse({'plan': to_plan(plan), 'reused': False}, status=201)
    except ValueError as exc:
        return reply(str(exc), 400)


def owned_item(request, item_id):
    return WorkoutPlanItem.objects.select_related('session__plan', 'exercise').filter(
        pk=item_id, session__plan__user=request.user).first()


@require_GET
def alternatives(request, item_id):
    denied = access(request)
    if denied is not None:
        return denied
    item = owned_item(request, item_id)
    if item is None:
        return reply('Workout item not found.', 404)
    plan = item.session.plan
    if is_stale(request.user, plan):
        return reply('Onboarding changed. Regenerate your workout before substituting.', 409)
    preference = ModulePreference.objects.get(user=request.user, module='workout')
    available = [to_exercise(e) for e in valid_exercises(preference, plan.avoid_tags)
                 if e.movement == item.exercise.movement and e.pk != item.exercise_id]
    return JsonResponse({'item_id': item.pk, 'alternatives': available})


@require_POST
def substitute(request, item_id):
    denied = access(request)
    if denied is not None:
        return denied
    try:
        data = payload(request)
        if set(data) != {'exercise_slug'} or not isinstance(data['exercise_slug'], str):
            raise ValueError('Provide an exercise_slug only.')
        with transaction.atomic():
            # Ownership determined solely from the signed-in user.
            item = (WorkoutPlanItem.objects.select_for_update()
                    .select_related('session__plan', 'exercise')
                    .filter(pk=item_id, session__plan__user=request.user).first())
            if item is None:
                return reply('Workout item not found.', 404)
            plan = item.session.plan
            if is_stale(request.user, plan):
                return reply('Onboarding changed. Regenerate your workout first.', 409)
            preference = ModulePreference.objects.get(user=request.user, module='workout')
            available = {e.slug: e for e in valid_exercises(preference, plan.avoid_tags)
                         if e.movement == item.exercise.movement}
            exercise = available.get(data['exercise_slug'])
            if not exercise:
                raise ValueError('That substitution is not allowed for this movement and your selected constraints.')
            item.exercise = exercise
            sets, reps, rest = safe_prescription(exercise, preference.experience, item.session.focus == 'mobility', plan.focus_mode, plan.pace)
            item.sets, item.reps, item.rest_seconds = sets, reps, rest
            item.save(update_fields=['exercise', 'sets', 'reps', 'rest_seconds'])
        return JsonResponse({'item': {'id': item.pk, 'exercise': to_exercise(exercise),
                                      'sets': sets, 'reps': reps, 'rest_seconds': rest}})
    except ValueError as exc:
        return reply(str(exc), 400)


@require_POST
def adjust_item(request, item_id):
    """Edit a suggestion, not completed workout data. Only bounded presets allowed."""
    denied = access(request)
    if denied is not None:
        return denied
    try:
        data = payload(request)
        if set(data) != {'sets', 'reps', 'rest_seconds'}:
            raise ValueError('Provide sets, reps and rest_seconds only.')
        sets, reps, rest = data['sets'], data['reps'], data['rest_seconds']
        if type(sets) is not int or not 1 <= sets <= 4 or not isinstance(reps, str) or reps not in REP_OPTIONS or type(rest) is not int or rest not in REST_OPTIONS:
            raise ValueError('Choose valid sets (1–4), repetition preset and rest (30–120 seconds).')
        with transaction.atomic():
            item = (WorkoutPlanItem.objects.select_for_update().select_related('session__plan').filter(
                pk=item_id, session__plan__user=request.user).first())
            if item is None:
                return reply('Workout item not found.', 404)
            if is_stale(request.user, item.session.plan):
                return reply('Onboarding changed. Regenerate your workout first.', 409)
            if item.session.focus == 'mobility' and sets > 2:
                raise ValueError('Gentle recovery activities are limited to two suggested sets.')
            item.sets, item.reps, item.rest_seconds = sets, reps, rest
            item.save(update_fields=['sets', 'reps', 'rest_seconds'])
        return JsonResponse({'item': {'id': item.pk, 'sets': sets, 'reps': reps, 'rest_seconds': rest}})
    except ValueError as exc:
        return reply(str(exc), 400)


@require_POST
def move_item(request, item_id):
    """Reorder suggestions within one session; ownership and uniqueness enforced."""
    denied = access(request)
    if denied is not None:
        return denied
    try:
        data = payload(request)
        if set(data) != {'direction'} or data['direction'] not in ('up', 'down'):
            raise ValueError('Direction must be up or down.')
        with transaction.atomic():
            item = (WorkoutPlanItem.objects.select_for_update().select_related('session__plan').filter(
                pk=item_id, session__plan__user=request.user).first())
            if item is None:
                return reply('Workout item not found.', 404)
            if is_stale(request.user, item.session.plan):
                return reply('Onboarding changed. Regenerate your workout first.', 409)
            positions = list(WorkoutPlanItem.objects.select_for_update().filter(session=item.session).order_by('position'))
            index = next(i for i, row in enumerate(positions) if row.pk == item.pk)
            next_index = index + (-1 if data['direction'] == 'up' else 1)
            if next_index < 0 or next_index >= len(positions):
                raise ValueError('Cannot move this exercise further in that direction.')
            other = positions[next_index]
            original = item.position
            target = other.position
            item.position = max(row.position for row in positions) + 1
            item.save(update_fields=['position'])
            other.position = original
            other.save(update_fields=['position'])
            item.position = target
            item.save(update_fields=['position'])
        return JsonResponse({'plan': to_plan(item.session.plan)})
    except ValueError as exc:
        return reply(str(exc), 400)
