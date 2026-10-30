from types import SimpleNamespace
from unittest.mock import patch

from django.conf import settings
from django.core.cache import caches
from django.core.cache.backends.db import DatabaseCache
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework.test import APIClient

from users.models import User
from users.throttles import AccountIPThrottle, PasswordResetEmailThrottle


TEST_RATES = {scope: '2/min' for scope in settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']}
TEST_REST = {**settings.REST_FRAMEWORK, 'NUM_PROXIES': 0, 'DEFAULT_THROTTLE_RATES': TEST_RATES}
TEST_CACHES = {
    **settings.CACHES,
    'auth_throttles': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'isolated-account-throttle-tests',
    },
}


@override_settings(CACHES=TEST_CACHES, REST_FRAMEWORK=TEST_REST)
class AccountThrottleTests(TestCase):
    def setUp(self):
        self.cache = caches['auth_throttles']
        self.cache.clear()
        self.addCleanup(self.cache.clear)
        self.api = APIClient()
        self.user = User.objects.create_user(
            email='throttle@example.com', name='Throttle Member',
            password='Throttle-horse-729!', is_verified=True,
        )

    def assert_throttled(self, response):
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.data['code'], 'throttled')
        self.assertIsInstance(response.data['detail'], str)
        self.assertGreater(response.data['retry_after'], 0)
        self.assertEqual(int(response['Retry-After']), response.data['retry_after'])

    def test_account_endpoints_enforce_limits_before_handling_requests(self):
        for path in [
            '/api/users/signin/', '/api/users/create/',
            '/api/users/forgetPassword/', '/api/users/resendVerification/',
            '/api/users/resetPassword/', '/api/users/verifyEmail/',
            '/api/users/getGoogleUsrInfo/', '/api/users/getFbUsrInfo/',
            '/api/users/getMsUsrInfo/',
        ]:
            with self.subTest(path=path):
                self.cache.clear()
                self.assertEqual(self.api.post(path, {}).status_code, 400)
                self.assertEqual(self.api.post(path, {}).status_code, 400)
                self.assert_throttled(self.api.post(path, {}))

    def test_invalid_password_attempts_are_counted(self):
        data = {'email': self.user.email, 'password': 'wrong-password'}
        self.assertEqual(self.api.post('/api/users/signin/', data).status_code, 400)
        self.assertEqual(self.api.post('/api/users/signin/', data).status_code, 400)
        self.assert_throttled(self.api.post('/api/users/signin/', data))

    def test_successful_login_is_counted_but_refresh_and_logout_remain_available(self):
        data = {'email': self.user.email, 'password': 'Throttle-horse-729!'}
        first = self.api.post('/api/users/signin/', data)
        second = self.api.post('/api/users/signin/', data)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assert_throttled(self.api.post('/api/users/signin/', data))
        self.assertEqual(self.api.post('/api/users/refresh/', {'refresh': first.data['refresh']}).status_code, 200)
        self.assertEqual(self.api.post('/api/users/logout/', {'refresh': first.data['refresh']}).status_code, 200)
        self.api.credentials(HTTP_AUTHORIZATION=f"Bearer {second.data['access']}")
        self.assertEqual(self.api.post('/api/users/validateUser/').status_code, 200)
        self.assert_throttled(self.api.post('/api/users/signin/', data))

    def test_password_and_social_logins_share_one_budget(self):
        self.api.post('/api/users/signin/', {})
        self.api.post('/api/users/getGoogleUsrInfo/', {})
        self.assert_throttled(self.api.post('/api/users/getFbUsrInfo/', {}))

    def test_another_ip_has_an_independent_budget(self):
        for _ in range(2):
            self.api.post('/api/users/signin/', {}, REMOTE_ADDR='198.51.100.1')
        self.assert_throttled(self.api.post('/api/users/signin/', {}, REMOTE_ADDR='198.51.100.1'))
        response = self.api.post('/api/users/signin/', {}, REMOTE_ADDR='198.51.100.2')
        self.assertEqual(response.status_code, 400)

    def test_forwarded_headers_cannot_bypass_direct_ip_limits(self):
        for index in range(2):
            self.api.post('/api/users/signin/', {}, HTTP_X_FORWARDED_FOR=f'198.51.100.{index}')
        self.assert_throttled(self.api.post('/api/users/signin/', {}, HTTP_X_FORWARDED_FOR='203.0.113.9'))

    @override_settings(REST_FRAMEWORK={**TEST_REST, 'NUM_PROXIES': 1})
    def test_configured_proxy_uses_the_last_forwarded_client_ip(self):
        for prefix in ['198.51.100.1', '198.51.100.2']:
            self.api.post('/api/users/signin/', {}, HTTP_X_FORWARDED_FOR=f'{prefix}, 203.0.113.1')
        self.assert_throttled(self.api.post('/api/users/signin/', {}, HTTP_X_FORWARDED_FOR='198.51.100.3, 203.0.113.1'))
        response = self.api.post('/api/users/signin/', {}, HTTP_X_FORWARDED_FOR='203.0.113.2')
        self.assertEqual(response.status_code, 400)

    def test_request_budget_recovers_after_the_window_expires(self):
        now = [100.0]
        with patch.object(AccountIPThrottle, 'timer', staticmethod(lambda: now[0])):
            self.api.post('/api/users/signin/', {})
            self.api.post('/api/users/signin/', {})
            self.assert_throttled(self.api.post('/api/users/signin/', {}))
            now[0] += 61
            self.assertEqual(self.api.post('/api/users/signin/', {}).status_code, 400)

    def test_limits_are_independent_between_account_actions(self):
        self.api.post('/api/users/signin/', {})
        self.api.post('/api/users/signin/', {})
        self.assert_throttled(self.api.post('/api/users/signin/', {}))
        self.assertEqual(self.api.post('/api/users/forgetPassword/', {}).status_code, 400)

    def test_email_limits_follow_the_recipient_across_different_ips(self):
        for endpoint in ['forgetPassword', 'resendVerification']:
            with self.subTest(endpoint=endpoint):
                self.cache.clear()
                path = f'/api/users/{endpoint}/'
                for email, ip in [('TARGET@example.com', '198.51.100.1'), (' target@example.com ', '198.51.100.2')]:
                    self.assertEqual(self.api.post(path, {'email': email}, REMOTE_ADDR=ip).status_code, 200)
                self.assert_throttled(self.api.post(path, {'email': 'target@example.com'}, REMOTE_ADDR='198.51.100.3'))
                self.assertEqual(self.api.post(path, {'email': 'other@example.com'}, REMOTE_ADDR='198.51.100.4').status_code, 200)

    @patch('users.views.send_account_action')
    def test_email_delivery_does_not_run_after_the_recipient_limit(self, send_action):
        for index in range(2):
            response = self.api.post('/api/users/forgetPassword/', {'email': self.user.email}, REMOTE_ADDR=f'198.51.100.{index}')
            self.assertEqual(response.status_code, 200)
        self.assert_throttled(self.api.post('/api/users/forgetPassword/', {'email': self.user.email}, REMOTE_ADDR='198.51.100.3'))
        self.assertEqual(send_action.call_count, 2)


@override_settings(CACHES=TEST_CACHES, REST_FRAMEWORK=TEST_REST)
class ThrottleIdentityTests(SimpleTestCase):
    def test_email_keys_are_normalized_and_do_not_contain_the_email(self):
        throttle = PasswordResetEmailThrottle()
        first = throttle.get_cache_key(SimpleNamespace(data={'email': ' MEMBER@example.com '}), None)
        second = throttle.get_cache_key(SimpleNamespace(data={'email': 'member@example.com'}), None)
        self.assertEqual(first, second)
        self.assertNotIn('member', first)
        self.assertNotIn('@', first)

    def test_invalid_email_values_do_not_create_recipient_counters(self):
        throttle = PasswordResetEmailThrottle()
        for data in [{}, {'email': []}, {'email': 'not-an-email'}, []]:
            self.assertIsNone(throttle.get_cache_key(SimpleNamespace(data=data), None))


@override_settings(
    CACHES={**TEST_CACHES, 'auth_throttles': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'test_auth_rate_limit_cache',
    }},
    REST_FRAMEWORK=TEST_REST,
)
class DatabaseThrottleCacheTests(TestCase):
    def test_independent_cache_instances_share_request_history(self):
        # This table is created only inside Django's disposable SQLite test DB.
        call_command('createcachetable', 'test_auth_rate_limit_cache', verbosity=0)
        first_worker = DatabaseCache('test_auth_rate_limit_cache', {})
        second_worker = DatabaseCache('test_auth_rate_limit_cache', {})
        api = APIClient()
        with patch.object(AccountIPThrottle, 'cache', first_worker):
            self.assertEqual(api.post('/api/users/signin/', {}).status_code, 400)
        with patch.object(AccountIPThrottle, 'cache', second_worker):
            self.assertEqual(api.post('/api/users/signin/', {}).status_code, 400)
            self.assertEqual(api.post('/api/users/signin/', {}).status_code, 429)
