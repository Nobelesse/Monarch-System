from unittest.mock import patch
from django.db import DatabaseError
from django.http import JsonResponse
from django.test import TestCase
from django.contrib.auth import get_user_model
class FoundationTests(TestCase):
    def test_database_health(self):
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['database'], 'connected')
    def test_database_failure_is_sanitized(self):
        with patch('core.views.connection.cursor', side_effect=DatabaseError('secret-password')):
            response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('secret-password', response.content.decode())
    def test_no_public_admin(self):
        self.assertEqual(self.client.get('/admin/').status_code, 404)
    def test_read_only_endpoints(self):
        self.assertEqual(self.client.post('/api/health/').status_code, 405)
        self.assertEqual(self.client.post('/api/system/').status_code, 405)
    def test_capabilities_are_honest(self):
        data = self.client.get('/api/system/').json()
        self.assertTrue(data['authentication_available'])
        self.assertFalse(data['public_access_ready'])
    def test_user_password_is_hashed(self):
        user = get_user_model().objects.create_user(username='test-player', password='test-password-not-real')
        self.assertNotEqual(user.password, 'test-password-not-real')
        self.assertTrue(user.check_password('test-password-not-real'))

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, override_settings
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
import json
from core.models import PlayerPaths, SocialIdentity
from core.auth_api import valid_paths
from config.admin_guard import LoopbackOnlyMiddleware

PASSWORD = 'StrongExampleOnly!9273'

class AccountTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client(enforce_csrf_checks=True)
        self.client.get('/api/auth/csrf/')
    def csrf_post(self, url, payload=None, method='post'):
        token = self.client.cookies.get('csrftoken').value if self.client.cookies.get('csrftoken') else ''
        if not token:
            self.client.get('/api/auth/csrf/')
            token = self.client.cookies['csrftoken'].value
        return getattr(self.client, method)(url, data=json.dumps(payload or {}), content_type='application/json', HTTP_X_CSRFTOKEN=token)
    def register(self, username='player1', email='player1@example.com', modules=None):
        return self.csrf_post('/api/auth/register/', {'username':username,'email':email,'password':PASSWORD,'modules':modules or ['workout']})
    def test_registration_and_session(self):
        r = self.register(modules=['workout', 'study'])
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(r.json()['user']['modules'], ['workout','study'])
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 200)
        self.assertNotEqual(get_user_model().objects.get(username='player1').password, PASSWORD)
    def test_password_policy(self):
        r = self.csrf_post('/api/auth/register/', {'username':'player1', 'email':'player1@example.com','password':'123'})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(get_user_model().objects.count(), 0)
    def test_case_insensitive_uniqueness(self):
        self.register()
        r = self.register(username='PLAYER1', email='OTHER@example.com')
        self.assertEqual(r.status_code, 409)
        r = self.register(username='other', email='PLAYER1@example.com')
        self.assertEqual(r.status_code, 409)
    def test_browser_session_cookie_is_not_persistent(self):
        from django.conf import settings
        self.assertTrue(settings.SESSION_EXPIRE_AT_BROWSER_CLOSE)
        self.register()
        session_cookie = self.client.cookies[settings.SESSION_COOKIE_NAME]
        self.assertFalse(session_cookie['expires'])

    def test_login_and_logout(self):
        self.register()
        self.csrf_post('/api/auth/logout/')
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 401)
        bad = self.csrf_post('/api/auth/login/', {'identifier':'player1@example.com','password':'bad'})
        self.assertEqual(bad.status_code, 401)
        good = self.csrf_post('/api/auth/login/', {'identifier':'PLAYER1@example.com','password':PASSWORD})
        self.assertEqual(good.status_code, 200, good.content)
        self.assertEqual(self.csrf_post('/api/auth/logout/').status_code, 200)
        self.assertEqual(self.client.get('/api/auth/me/').status_code, 401)
    def test_registration_from_vite_origin_through_proxy(self):
        # Real Chrome POSTs carry Origin: 127.0.0.1:5173 while Vite changes
        # the proxied Host to Django's 127.0.0.1:8000.  The old configuration
        # responded with the default HTML CSRF 403 page and broke JSON parsing.
        csrf_token = self.client.cookies['csrftoken'].value
        response = self.client.post(
            '/api/auth/register/',
            data=json.dumps({'username': 'originplayer', 'email': 'origin@example.com',
                             'password': PASSWORD, 'modules': ['study']}),
            content_type='application/json',
            HTTP_HOST='127.0.0.1:8000',
            HTTP_ORIGIN='http://127.0.0.1:5173',
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.json()['user']['username'], 'originplayer')

    def test_untrusted_origin_stays_rejected(self):
        csrf_token = self.client.cookies['csrftoken'].value
        response = self.client.post(
            '/api/auth/register/', data='{}', content_type='application/json',
            HTTP_HOST='127.0.0.1:8000', HTTP_ORIGIN='http://untrusted.example',
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_csrf_required_even_for_anonymous_registration(self):
        naked = Client(enforce_csrf_checks=True)
        r = naked.post('/api/auth/register/', data='{}',content_type='application/json')
        self.assertEqual(r.status_code, 403)
    def test_csrf_required_for_authenticated_changes(self):
        self.register()
        r = self.client.put('/api/paths/', data='{"modules":["study"]}', content_type='application/json')
        self.assertEqual(r.status_code, 403)
    def test_guest_cannot_read_or_mutate_paths(self):
        self.assertEqual(self.client.get('/api/paths/').status_code, 401)
        self.assertEqual(self.csrf_post('/api/paths/',{'modules':['workout']},'put').status_code, 401)
    def test_account_owned_path_save(self):
        self.register()
        r = self.csrf_post('/api/paths/',{'modules':['learning','study']},'put')
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(self.client.get('/api/paths/').json()['modules'], ['learning','study'])
    def test_invalid_paths_rejected(self):
        self.register()
        for values in ([], ['study', 'study'], ['hacking'], ['workout','study','learning','other']):
            self.assertEqual(self.csrf_post('/api/paths/',{'modules':values},'put').status_code, 400)
    def test_two_user_isolation(self):
        self.register(username='alice',email='alice@example.com',modules=['study'])
        alice_id = get_user_model().objects.get(username='alice').pk
        self.csrf_post('/api/auth/logout/')
        self.register(username='bob',email='bob@example.com',modules=['learning'])
        self.assertEqual(self.client.get('/api/paths/').json()['modules'], ['learning'])
        self.csrf_post('/api/paths/',{'modules':['workout']},'put')
        self.assertEqual(PlayerPaths.objects.get(user_id=alice_id).modules, ['study'])
        self.assertEqual(self.client.get('/api/auth/me/').json()['user']['username'], 'bob')
    def test_invalid_json_and_oversized_request(self):
        self.register()
        csrf = self.client.cookies['csrftoken'].value
        bad = self.client.put('/api/paths/',data='not-json',content_type='application/json',HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(bad.status_code, 400)
        huge = self.client.put('/api/paths/',data='x'*9000,content_type='application/json',HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(huge.status_code, 400)
    def test_login_throttled(self):
        self.register()
        self.csrf_post('/api/auth/logout/')
        for _ in range(8):
            self.csrf_post('/api/auth/login/',{'identifier':'player1','password':'wrong'})
        self.assertEqual(self.csrf_post('/api/auth/login/',{'identifier':'player1','password':PASSWORD}).status_code, 429)
    def test_public_admin_remains_absent(self):
        self.assertEqual(self.client.get('/admin/').status_code, 404)

class GoogleTests(TestCase):
    setUp = AccountTests.setUp
    csrf_post = AccountTests.csrf_post
    register = AccountTests.register
    # inherit account setup and tests while adding social auth checks
    @override_settings(GOOGLE_CLIENT_ID='test-google-client-id')
    @patch('core.auth_api.verify_google')
    def test_google_account_creation_and_reuse(self, verifier):
        verifier.return_value = {'iss':'accounts.google.com','sub':'google-123','email_verified':True,'email':'google@example.com'}
        r = self.csrf_post('/api/auth/google/', {'credential':'x'*200})
        self.assertEqual(r.status_code, 200, r.content)
        u = get_user_model().objects.get(email='google@example.com')
        self.assertFalse(u.has_usable_password())
        self.csrf_post('/api/auth/logout/')
        r = self.csrf_post('/api/auth/google/', {'credential':'x'*200})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['user']['id'], u.pk)
    @override_settings(GOOGLE_CLIENT_ID='test-google-client-id')
    @patch('core.auth_api.verify_google')
    def test_google_does_not_silently_link_same_email(self, verifier):
        verifier.return_value = {'iss':'accounts.google.com','sub':'another-id','email_verified':True,'email':'player1@example.com'}
        self.register()
        self.csrf_post('/api/auth/logout/')
        r=self.csrf_post('/api/auth/google/',{'credential':'x'*200})
        self.assertEqual(r.status_code, 409)
        self.assertEqual(SocialIdentity.objects.count(), 0)
    @override_settings(GOOGLE_CLIENT_ID='test-google-client-id')
    @patch('core.auth_api.verify_google')
    def test_explicit_google_link(self, verifier):
        verifier.return_value = {'iss':'https://accounts.google.com','sub':'g-1','email_verified':True,'email':'player1@example.com'}
        self.register()
        r = self.csrf_post('/api/auth/google/link/',{'credential':'x'*200})
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(SocialIdentity.objects.count(), 1)
    @override_settings(GOOGLE_CLIENT_ID='test-google-client-id')
    @patch('core.auth_api.verify_google')
    def test_google_verified_email_required(self, verifier):
        verifier.return_value = {'iss':'accounts.google.com','sub':'g-1','email_verified':False,'email':'a@example.com'}
        self.assertEqual(self.csrf_post('/api/auth/google/',{'credential':'x'*200}).status_code,400)
    def test_google_requires_configuration(self):
        self.assertEqual(self.csrf_post('/api/auth/google/',{'credential':'x'*200}).status_code,400)

class AdminIsolationTests(TestCase):
    def test_admin_does_not_trust_public_frontend_origin(self):
        from config import admin_settings
        self.assertNotIn('http://127.0.0.1:5173', admin_settings.CSRF_TRUSTED_ORIGINS)
    def test_nonlocal_admin_request_forbidden(self):
        request = RequestFactory().get('/admin/', REMOTE_ADDR='10.0.0.24')
        res = LoopbackOnlyMiddleware(lambda r: JsonResponse({'ok':True}))(request)
        self.assertEqual(res.status_code, 403)
    def test_local_request_allowed(self):
        request = RequestFactory().get('/admin/', REMOTE_ADDR='127.0.0.1')
        res = LoopbackOnlyMiddleware(lambda r: JsonResponse({'ok':True}))(request)
        self.assertEqual(res.status_code, 200)


from core.models import PlayerProfile, ModulePreference, WeeklyAvailability, PrivatePhysique


class OnboardingTests(TestCase):
    """Phase 3 integration, privacy and negative security tests."""
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.client.get('/api/auth/csrf/')
        self.password = PASSWORD

    def send(self, url, data, method='put', csrf=True, **headers):
        token = self.client.cookies['csrftoken'].value
        return getattr(self.client, method)(url, data=json.dumps(data), content_type='application/json',
            **({'HTTP_X_CSRFTOKEN': token} if csrf else {}), **headers)

    def register(self, username='onboarder', modules=None):
        r = self.send('/api/auth/register/', {'username': username, 'email': f'{username}@example.com',
            'password': PASSWORD, 'modules': modules or ['workout']}, method='post')
        self.assertEqual(r.status_code, 201, r.content)
        return r.json()['user']['id']

    def setup_data(self, modules=('workout',), completed=True):
        prefs = {module: {'goal': 'Build steady habits', 'experience': 'beginner',
            'equipment': ['bodyweight'] if module == 'workout' else [],
            'topics': [] if module == 'workout' else ['Python']} for module in modules}
        return {'display_name': 'My Monarch', 'timezone': 'Asia/Kolkata', 'language': 'en',
            'reduced_motion': True, 'high_contrast': False, 'current_step': 5, 'completed': completed,
            'preferences': prefs, 'schedule': [{'module': m, 'weekday': 1, 'minutes': 45} for m in modules],
            'physique': {'height_cm': 175.0 if 'workout' in modules else None,
                         'weight_kg': 70.0 if 'workout' in modules else None}}

    def test_guest_requires_authentication(self):
        self.assertEqual(self.client.get('/api/onboarding/').status_code, 401)
        self.assertEqual(self.send('/api/onboarding/', self.setup_data()).status_code, 401)

    def test_csrf_required_for_onboarding_write(self):
        self.register()
        self.assertEqual(self.send('/api/onboarding/', self.setup_data(), csrf=False).status_code, 403)

    def test_initial_draft_and_get_are_account_scoped(self):
        self.register()
        r = self.client.get('/api/onboarding/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['modules'], ['workout'])
        self.assertFalse(r.json()['onboarding']['completed'])
        self.assertEqual(r.json()['onboarding']['preferences']['workout']['goal'], '')
        self.assertEqual(PlayerProfile.objects.count(), 1)

    def test_save_draft_and_resume(self):
        self.register(modules=['study', 'learning'])
        data = self.setup_data(('study','learning'), completed=False)
        data['current_step'] = 3
        r = self.send('/api/onboarding/', data)
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(self.client.get('/api/onboarding/').json()['onboarding']['current_step'], 3)
        self.assertEqual(ModulePreference.objects.count(), 2)
        self.assertEqual(WeeklyAvailability.objects.count(), 2)
        self.assertFalse(r.json()['onboarding']['completed'])

    def test_completion_and_repeated_save_idempotent(self):
        self.register(modules=['workout', 'study', 'learning'])
        data = self.setup_data(('workout','study','learning'))
        for _ in range(2):
            r = self.send('/api/onboarding/', data)
            self.assertEqual(r.status_code, 200, r.content)
            self.assertTrue(r.json()['onboarding']['completed'])
        self.assertEqual(ModulePreference.objects.count(), 3)
        self.assertEqual(WeeklyAvailability.objects.count(), 3)
        self.assertEqual(PrivatePhysique.objects.count(), 1)

    def test_completion_requires_goal_and_schedule_for_every_module(self):
        self.register(modules=['workout','study'])
        data=self.setup_data(('workout','study'))
        data['preferences']['study']['goal']=''
        self.assertEqual(self.send('/api/onboarding/', data).status_code, 400)
        self.assertEqual(ModulePreference.objects.count(), 0)
        data['preferences']['study']['goal']='Pass exam'
        data['schedule'] = data['schedule'][:1]
        self.assertEqual(self.send('/api/onboarding/', data).status_code, 400)
        self.assertEqual(WeeklyAvailability.objects.count(), 0)

    def test_field_validation_cannot_modify_owner(self):
        self.register()
        data=self.setup_data()
        data['user_id']=9999
        self.assertEqual(self.send('/api/onboarding/', data).status_code, 400)
        self.assertEqual(PlayerProfile.objects.count(), 0)

    def test_cross_account_isolation_private_physique(self):
        first=self.register(username='first')
        self.assertEqual(self.send('/api/onboarding/', self.setup_data()).status_code, 200)
        self.send('/api/auth/logout/', {}, method='post')
        second=self.register(username='second',modules=['learning'])
        result=self.client.get('/api/onboarding/').json()
        self.assertIsNone(result['onboarding']['physique']['height_cm'])
        self.assertNotIn('workout', result['onboarding']['preferences'])
        self.assertEqual(PrivatePhysique.objects.count(), 1)
        self.assertEqual(PrivatePhysique.objects.get().user_id, first)
        self.assertNotEqual(first,second)

    def test_physique_never_exposed_in_account_or_public_api(self):
        self.register()
        self.send('/api/onboarding/', self.setup_data())
        self.assertNotIn('height_cm', self.client.get('/api/auth/me/').content.decode())
        self.assertNotIn('height_cm', self.client.get('/api/system/').content.decode())

    def test_clear_private_data(self):
        self.register()
        data=self.setup_data()
        self.send('/api/onboarding/', data)
        data['physique']={'height_cm': None, 'weight_kg': None}
        self.assertEqual(self.send('/api/onboarding/', data).status_code, 200)
        self.assertEqual(PrivatePhysique.objects.count(), 0)

    def test_invalid_types_rejected_without_partial_updates(self):
        self.register()
        invalids = [
            ('language', []), ('timezone', 'Mars/Olympus'), ('current_step', True),
            ('high_contrast', 'yes')
        ]
        for field, value in invalids:
            data=self.setup_data();data[field]=value
            self.assertEqual(self.send('/api/onboarding/', data).status_code, 400, field)
        self.assertEqual(ModulePreference.objects.count(),0)

    def test_duplicate_day_rejected(self):
        self.register()
        data=self.setup_data()
        data['schedule'].append(dict(data['schedule'][0]))
        self.assertEqual(self.send('/api/onboarding/',data).status_code,400)

    def test_schedule_rejects_bool_and_fractions(self):
        self.register()
        for field,val in [('weekday', True),('minutes',True),('minutes',13),('minutes',22)]:
            data=self.setup_data()
            data['schedule'][0][field]=val
            self.assertEqual(self.send('/api/onboarding/',data).status_code,400)

    def test_unselected_module_rejected(self):
        self.register(modules=['study'])
        data=self.setup_data(('study',))
        data['preferences']['workout'] = self.setup_data()['preferences']['workout']
        self.assertEqual(self.send('/api/onboarding/',data).status_code,400)

    def test_changing_paths_reopens_onboarding(self):
        self.register()
        self.assertEqual(self.send('/api/onboarding/',self.setup_data()).status_code,200)
        r=self.send('/api/paths/',{'modules':['workout','study']})
        self.assertEqual(r.status_code,200,r.content)
        self.assertFalse(self.client.get('/api/onboarding/').json()['onboarding']['completed'])

    def test_untrusted_browser_origin_rejected(self):
        self.register()
        r=self.send('/api/onboarding/',self.setup_data(),HTTP_HOST='127.0.0.1:8000',
             HTTP_ORIGIN='https://evil.example')
        self.assertEqual(r.status_code,403)

    def test_public_admin_not_exposed(self):
        self.register()
        self.assertEqual(self.client.get('/admin/').status_code,404)

    def test_completed_onboarding_survives_logout_and_next_login(self):
        self.register()
        saved = self.send('/api/onboarding/', self.setup_data())
        self.assertEqual(saved.status_code, 200, saved.content)
        self.assertTrue(saved.json()['onboarding']['completed'])
        self.assertEqual(self.send('/api/auth/logout/', {}, method='post').status_code, 200)
        self.assertEqual(self.client.get('/api/onboarding/').status_code, 401)
        authenticated = self.send('/api/auth/login/', {'identifier': 'onboarder', 'password': PASSWORD}, method='post')
        self.assertEqual(authenticated.status_code, 200, authenticated.content)
        restored = self.client.get('/api/onboarding/')
        self.assertTrue(restored.json()['onboarding']['completed'])
        self.assertEqual(restored.json()['onboarding']['display_name'], 'My Monarch')

    def test_completed_profile_remains_complete_after_valid_edits(self):
        self.register()
        saved = self.send('/api/onboarding/', self.setup_data())
        self.assertEqual(saved.status_code, 200, saved.content)
        edits = self.setup_data()
        edits['display_name'] = 'Monarch Updated'
        updated = self.send('/api/onboarding/', edits)
        self.assertEqual(updated.status_code, 200, updated.content)
        self.assertTrue(updated.json()['onboarding']['completed'])
        self.assertEqual(updated.json()['onboarding']['display_name'], 'Monarch Updated')

from django.utils import timezone
from core.models import WorkoutExercise, WorkoutPlan, WorkoutSession, WorkoutPlanItem
from core.workout_api import pick_strength_days


class WorkoutEngineTests(TestCase):
    """Phase 4: API, data ownership, conservative scheduling and substitutions."""
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.client.get('/api/auth/csrf/')

    def post_json(self, path, data, client=None, csrf=True):
        browser = client or self.client
        if not browser.cookies.get('csrftoken'):
            browser.get('/api/auth/csrf/')
        headers = {'HTTP_X_CSRFTOKEN': browser.cookies['csrftoken'].value} if csrf else {}
        return browser.post(path, data=json.dumps(data), content_type='application/json', **headers)

    def make_user(self, name='trainee', modules=None):
        res = self.post_json('/api/auth/register/', {
            'username': name, 'email': name + '@example.com', 'password': PASSWORD,
            'modules': modules or ['workout']})
        self.assertEqual(res.status_code, 201, res.content)
        return get_user_model().objects.get(username=name)

    def onboard(self, user, days=(0, 2, 4), experience='beginner', equipment=None, completed=True):
        PlayerProfile.objects.update_or_create(user=user, defaults={
            'display_name': 'Trainee', 'completed_at': timezone.now() if completed else None})
        ModulePreference.objects.update_or_create(user=user, module='workout', defaults={
            'goal': 'Build a sustainable routine', 'experience': experience,
            'equipment': equipment or [], 'topics': []})
        WeeklyAvailability.objects.filter(user=user, module='workout').delete()
        WeeklyAvailability.objects.bulk_create([
            WeeklyAvailability(user=user,module='workout',weekday=day,minutes=45) for day in days])

    def generate(self, tags=None, regenerate=False, acknowledged=True):
        return self.post_json('/api/workout/plan/generate/', {
            'avoid_tags': tags or [], 'acknowledged': acknowledged, 'regenerate': regenerate})

    def test_guest_cannot_read_or_write(self):
        self.assertEqual(self.client.get('/api/workout/library/').status_code, 401)
        self.assertEqual(self.client.get('/api/workout/plan/').status_code, 401)
        self.assertEqual(self.generate().status_code, 401)

    def test_nonworkout_account_cannot_use_api(self):
        self.make_user(modules=['study'])
        self.assertEqual(self.client.get('/api/workout/library/').status_code, 403)
        self.assertEqual(self.generate().status_code, 403)

    def test_seeded_catalog_has_complete_instructions(self):
        self.make_user()
        r = self.client.get('/api/workout/library/')
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(r.json()['exercises']), 25)
        self.assertTrue(all(e['instructions'] for e in r.json()['exercises']))

    def test_onboarding_must_be_complete(self):
        self.make_user()
        self.assertEqual(self.generate().status_code, 400)
        self.assertEqual(WorkoutPlan.objects.count(), 0)

    def test_missing_preference_or_schedule_rejected(self):
        user = self.make_user()
        self.onboard(user)
        ModulePreference.objects.filter(user=user,module='workout').delete()
        self.assertEqual(self.generate().status_code, 400)
        self.onboard(user)
        WeeklyAvailability.objects.filter(user=user,module='workout').delete()
        self.assertEqual(self.generate().status_code, 400)

    def test_generation_matches_weekdays_and_limits(self):
        user = self.make_user()
        self.onboard(user,days=(0,1,2,3,4,5,6))
        result = self.generate()
        self.assertEqual(result.status_code, 201, result.content)
        days = result.json()['plan']['days']
        self.assertEqual([d['weekday'] for d in days],list(range(7)))
        self.assertLessEqual(sum(d['focus']=='strength' for d in days), 3)
        self.assertTrue(all(d['planned_minutes'] <= 60 for d in days))
        self.assertTrue(all(1 <= len(d['items']) <= 5 for d in days))
        for day in days:
            if day['focus']=='mobility':
                self.assertTrue(all(i['exercise']['movement']=='mobility' for i in day['items']))

    def test_strength_days_are_nonadjacent_in_circular_week(self):
        strength = pick_strength_days([0,1,2,3,4,5,6])
        self.assertLessEqual(len(strength), 3)
        for day in strength:
            self.assertNotIn((day+1)%7, strength)
            self.assertNotIn((day-1)%7, strength)

    def test_no_external_equipment_selected(self):
        user = self.make_user()
        self.onboard(user, equipment=[])
        response = self.generate()
        self.assertEqual(response.status_code, 201, response.content)
        for day in response.json()['plan']['days']:
            for item in day['items']:
                self.assertEqual(item['exercise']['equipment'], 'bodyweight')

    def test_exclusions_respected(self):
        user = self.make_user()
        self.onboard(user,days=(0,2,4,5))
        result = self.generate(tags=['floor','knee','wrist'])
        self.assertEqual(result.status_code, 201, result.content)
        for day in result.json()['plan']['days']:
            for item in day['items']:
                self.assertFalse({'floor','knee','wrist'} & set(item['exercise']['caution_tags']))

    def test_short_session_not_overfilled(self):
        user=self.make_user()
        self.onboard(user,days=(1,))
        WeeklyAvailability.objects.filter(user=user,module='workout').update(minutes=15)
        res=self.generate()
        self.assertEqual(res.status_code, 201, res.content)
        self.assertEqual(res.json()['plan']['days'][0]['planned_minutes'],15)
        self.assertEqual(len(res.json()['plan']['days'][0]['items']),1)

    def test_plan_get_is_private_and_saved(self):
        user=self.make_user()
        self.onboard(user)
        generated=self.generate().json()['plan']
        viewed=self.client.get('/api/workout/plan/').json()['plan']
        self.assertEqual(viewed['id'], generated['id'])
        self.assertFalse(viewed['stale'])
        self.assertEqual(WorkoutPlan.objects.count(),1)

    def test_repeated_generation_is_idempotent_by_default(self):
        user=self.make_user()
        self.onboard(user)
        first=self.generate().json()['plan']
        second=self.generate()
        self.assertTrue(second.json()['reused'])
        self.assertEqual(first['id'],second.json()['plan']['id'])
        self.assertEqual(WorkoutSession.objects.count(),3)

    def test_regeneration_can_refresh_same_draft_without_duplicates(self):
        user=self.make_user()
        self.onboard(user)
        first=self.generate().json()['plan']
        second=self.generate(regenerate=True).json()['plan']
        self.assertEqual(first['id'], second['id'])
        self.assertEqual(WorkoutPlan.objects.count(),1)
        self.assertEqual(WorkoutSession.objects.count(),3)

    def test_invalid_inputs_rejected_without_deleting_draft(self):
        user=self.make_user()
        self.onboard(user)
        self.generate()
        for data in (
            {'avoid_tags':['unknown'],'acknowledged':True,'regenerate':False},
            {'avoid_tags':['knee','knee'],'acknowledged':True,'regenerate':False},
            {'avoid_tags':[],'acknowledged':False,'regenerate':False},
            {'avoid_tags':[],'acknowledged':True,'regenerate':'yes'},
            {'avoid_tags':[],'acknowledged':True,'regenerate':False,'user_id':123}):
            self.assertEqual(self.post_json('/api/workout/plan/generate/',data).status_code,400)
        self.assertEqual(WorkoutPlan.objects.count(),1)
        self.assertEqual(WorkoutSession.objects.count(),3)

    def test_csrf_required(self):
        user=self.make_user()
        self.onboard(user)
        r=self.post_json('/api/workout/plan/generate/',{
            'avoid_tags':[],'acknowledged':True,'regenerate':False},csrf=False)
        self.assertEqual(r.status_code,403)

    def test_substitution_same_pattern_and_saved(self):
        user=self.make_user()
        self.onboard(user,days=(0,2,4),equipment=['dumbbells','resistance_bands'])
        first=self.generate().json()['plan']
        item=next((x for d in first['days'] for x in d['items'] if x['exercise']['movement']=='pull'),None)
        self.assertIsNotNone(item)
        options=self.client.get(f'/api/workout/items/{item["id"]}/alternatives/')
        self.assertEqual(options.status_code,200)
        self.assertTrue(options.json()['alternatives'])
        replacement=options.json()['alternatives'][0]
        changed=self.post_json(f'/api/workout/items/{item["id"]}/substitute/',{'exercise_slug':replacement['slug']})
        self.assertEqual(changed.status_code,200,changed.content)
        saved=WorkoutPlanItem.objects.get(pk=item['id'])
        self.assertEqual(saved.exercise.slug,replacement['slug'])

    def test_substitution_cannot_cross_movement_or_user_filters(self):
        user=self.make_user()
        self.onboard(user)
        day=self.generate().json()['plan']['days'][0]
        item=day['items'][0]
        blocked=self.post_json(f'/api/workout/items/{item["id"]}/substitute/',{'exercise_slug':'seated-shoulder-circles'})
        # If original item happens to be mobility, choose a definite wrong group.
        if item['exercise']['movement']=='mobility':
            blocked=self.post_json(f'/api/workout/items/{item["id"]}/substitute/',{'exercise_slug':'chair-sit-to-stand'})
        self.assertEqual(blocked.status_code,400)

    def test_different_user_cannot_read_or_replace_first_users_items(self):
        first_user=self.make_user(name='first')
        self.onboard(first_user)
        item_id=self.generate().json()['plan']['days'][0]['items'][0]['id']
        self.post_json('/api/auth/logout/',{})
        second_user=self.make_user(name='second')
        self.onboard(second_user)
        self.assertIsNone(self.client.get('/api/workout/plan/').json()['plan'])
        self.assertEqual(self.client.get(f'/api/workout/items/{item_id}/alternatives/').status_code,404)
        self.assertEqual(self.post_json(f'/api/workout/items/{item_id}/substitute/',{'exercise_slug':'wall-pushup'}).status_code,404)

    def test_onboarding_changes_mark_plan_stale(self):
        user=self.make_user()
        self.onboard(user)
        item_id=self.generate().json()['plan']['days'][0]['items'][0]['id']
        ModulePreference.objects.filter(user=user,module='workout').update(experience='intermediate')
        self.assertTrue(self.client.get('/api/workout/plan/').json()['plan']['stale'])
        self.assertEqual(self.client.get(f'/api/workout/items/{item_id}/alternatives/').status_code,409)
        self.assertEqual(self.post_json(f'/api/workout/items/{item_id}/substitute/',{'exercise_slug':'wall-pushup'}).status_code,409)
        self.assertEqual(self.generate().status_code,201)
        self.assertFalse(self.client.get('/api/workout/plan/').json()['plan']['stale'])

    def test_preserve_registration_and_onboarding_routes(self):
        self.make_user()
        self.assertEqual(self.client.get('/api/auth/me/').status_code,200)
        self.assertEqual(self.client.get('/api/onboarding/').status_code,200)
        self.assertEqual(self.client.get('/admin/').status_code,404)

class WorkoutRefinementTests(TestCase):
    setUp = WorkoutEngineTests.setUp
    post_json = WorkoutEngineTests.post_json
    make_user = WorkoutEngineTests.make_user
    onboard = WorkoutEngineTests.onboard
    generate = WorkoutEngineTests.generate
    """Phase 4.1: bounded customization, explicit training focus, owned editing."""

    def test_expanded_catalog_contains_new_movements(self):
        self.make_user()
        result = self.client.get('/api/workout/library/')
        self.assertEqual(result.status_code, 200)
        self.assertGreaterEqual(len(result.json()['exercises']), 60)
        self.assertTrue(WorkoutExercise.objects.filter(slug='band-chest-press').exists())

    def test_focus_and_pace_persist_in_plan_and_signature(self):
        user = self.make_user()
        self.onboard(user)
        result = self.post_json('/api/workout/plan/generate/', {
            'avoid_tags': [], 'acknowledged': True, 'regenerate': False,
            'focus_mode': 'strength', 'pace': 'easy'})
        self.assertEqual(result.status_code, 201, result.content)
        plan = result.json()['plan']
        self.assertEqual(plan['focus_mode'], 'strength')
        self.assertEqual(plan['pace'], 'easy')
        self.assertTrue(all(d['planned_minutes'] <= 40 for d in plan['days']))
        self.assertTrue(all(i['sets'] <= 2 for d in plan['days'] for i in d['items']))
        self.assertEqual(self.client.get('/api/workout/plan/').json()['plan']['focus_mode'], 'strength')

    def test_explicit_focus_modifies_weekly_split(self):
        user = self.make_user()
        self.onboard(user, days=(0,1,2,3,4,5,6))
        res = self.post_json('/api/workout/plan/generate/', {
            'avoid_tags': [], 'acknowledged': True, 'regenerate': False,
            'focus_mode': 'mobility', 'pace': 'standard'})
        self.assertEqual(res.status_code, 201, res.content)
        days = res.json()['plan']['days']
        self.assertLessEqual(sum(d['focus']=='strength' for d in days), 2)
        self.assertEqual(sum(d['focus']=='mobility' for d in days), 5)

    def test_upper_lower_split_and_permitted_categories(self):
        user = self.make_user()
        self.onboard(user, days=(0,2))
        res = self.generate()
        self.assertEqual(res.status_code, 201, res.content)
        days = res.json()['plan']['days']
        self.assertEqual([d['theme'] for d in days], ['upper', 'lower'])
        self.assertTrue(all(x['exercise']['movement'] in ('push','pull','core') for x in days[0]['items']))
        self.assertTrue(all(x['exercise']['movement'] in ('squat','hinge','core') for x in days[1]['items']))

    def test_invalid_focus_and_pace_do_not_destroy_existing(self):
        user = self.make_user()
        self.onboard(user)
        first = self.generate().json()['plan']['id']
        for focus, pace in (('expert','easy'),('strength','fast'),(123,'standard'),('mobility',None)):
            r = self.post_json('/api/workout/plan/generate/', {
                'avoid_tags': [], 'acknowledged': True, 'regenerate': True,
                'focus_mode': focus, 'pace': pace})
            self.assertEqual(r.status_code, 400)
        self.assertEqual(WorkoutPlan.objects.get(user=user).pk, first)

    def test_adjustment_persists_after_refresh(self):
        user = self.make_user()
        self.onboard(user)
        item = self.generate().json()['plan']['days'][0]['items'][0]
        res = self.post_json(f'/api/workout/items/{item["id"]}/adjust/', {
            'sets': 2, 'reps': '8–12 controlled', 'rest_seconds': 90})
        self.assertEqual(res.status_code, 200, res.content)
        record = WorkoutPlanItem.objects.get(pk=item['id'])
        self.assertEqual(record.sets, 2)
        self.assertEqual(record.reps, '8–12 controlled')
        self.assertEqual(record.rest_seconds, 90)
        self.assertEqual(self.client.get('/api/workout/plan/').json()['plan']['days'][0]['items'][0]['rest_seconds'], 90)

    def test_bad_adjustment_rejected(self):
        user = self.make_user()
        self.onboard(user)
        item = self.generate().json()['plan']['days'][0]['items'][0]
        for data in ({'sets': 9, 'reps': '8–12 controlled', 'rest_seconds': 90},
                     {'sets': True, 'reps': '8–12 controlled', 'rest_seconds': 90},
                     {'sets': 2, 'reps': '1000 until exhaustion', 'rest_seconds': 30},
                     {'sets': 2, 'reps': '8–12 controlled', 'rest_seconds': 500},
                     {'sets': 2, 'reps': '8–12 controlled', 'rest_seconds': 75, 'user_id': 999}):
            self.assertEqual(self.post_json(f'/api/workout/items/{item["id"]}/adjust/', data).status_code, 400)
        self.assertEqual(WorkoutPlanItem.objects.get(pk=item['id']).sets, item['sets'])

    def test_move_changes_only_order_without_losing_items(self):
        user = self.make_user()
        self.onboard(user)
        day = self.generate().json()['plan']['days'][0]
        self.assertGreaterEqual(len(day['items']), 2)
        first, second = day['items'][:2]
        result = self.post_json(f'/api/workout/items/{second["id"]}/move/', {'direction': 'up'})
        self.assertEqual(result.status_code, 200, result.content)
        ordered = result.json()['plan']['days'][0]['items']
        self.assertEqual(ordered[0]['id'], second['id'])
        self.assertEqual(ordered[1]['id'], first['id'])
        self.assertEqual({i['id'] for i in ordered}, {i['id'] for i in day['items']})

    def test_move_boundaries_and_invalid_requests(self):
        user = self.make_user()
        self.onboard(user)
        item = self.generate().json()['plan']['days'][0]['items'][0]
        path = f'/api/workout/items/{item["id"]}/move/'
        self.assertEqual(self.post_json(path, {'direction': 'up'}).status_code, 400)
        self.assertEqual(self.post_json(path, {'direction': 'sideways'}).status_code, 400)
        self.assertEqual(self.post_json(path, {'direction': 'down', 'user_id': 123}).status_code, 400)

    def test_other_account_cannot_adjust_or_move(self):
        owner = self.make_user(name='owner41')
        self.onboard(owner)
        item = self.generate().json()['plan']['days'][0]['items'][0]
        self.post_json('/api/auth/logout/', {})
        other = self.make_user(name='other41')
        self.onboard(other)
        self.assertEqual(self.post_json(f'/api/workout/items/{item["id"]}/adjust/',
            {'sets': 2,'reps':'8–12 controlled','rest_seconds':90}).status_code, 404)
        self.assertEqual(self.post_json(f'/api/workout/items/{item["id"]}/move/',
            {'direction':'down'}).status_code, 404)

    def test_onboarding_change_blocks_edits(self):
        user = self.make_user()
        self.onboard(user)
        item = self.generate().json()['plan']['days'][0]['items'][0]
        ModulePreference.objects.filter(user=user, module='workout').update(experience='intermediate')
        self.assertEqual(self.post_json(f'/api/workout/items/{item["id"]}/adjust/',
            {'sets':2,'reps':'8–12 controlled','rest_seconds':90}).status_code, 409)
        self.assertEqual(self.post_json(f'/api/workout/items/{item["id"]}/move/',
            {'direction':'down'}).status_code, 409)

    def test_new_write_endpoints_require_csrf(self):
        user = self.make_user()
        self.onboard(user)
        item = self.generate().json()['plan']['days'][0]['items'][0]
        self.assertEqual(self.post_json(f'/api/workout/items/{item["id"]}/adjust/',
            {'sets':2,'reps':'8–12 controlled','rest_seconds':90}, csrf=False).status_code, 403)
        self.assertEqual(self.post_json(f'/api/workout/items/{item["id"]}/move/',
            {'direction':'down'}, csrf=False).status_code, 403)
