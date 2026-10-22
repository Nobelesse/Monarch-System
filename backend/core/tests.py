from unittest.mock import patch
from django.db import DatabaseError
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
        self.assertFalse(data['authentication_available'])
        self.assertFalse(data['public_access_ready'])
    def test_user_password_is_hashed(self):
        user = get_user_model().objects.create_user(username='test-player', password='test-password-not-real')
        self.assertNotEqual(user.password, 'test-password-not-real')
        self.assertTrue(user.check_password('test-password-not-real'))
