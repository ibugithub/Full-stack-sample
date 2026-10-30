import os
import time
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

import requests
from django.contrib.auth import SESSION_KEY as AUTH_SESSION_KEY
from django.contrib.auth.models import Permission
from django.http import HttpResponse
from django.test import Client, TestCase, override_settings

from users.admin_google import SESSION_KEY, STATE_MAX_AGE
from users.models import User


@override_settings(FRONTEND_BASE_URL='http://testserver')
@patch.dict(os.environ, {
    'GOOGLE_CLIENT_ID': 'example-client', 'GOOGLE_CLIENT_SECRET': 'example-secret',
    'GOOGLE_REDIRECT_URI': 'accounts/googleCallback',
})
class GoogleAdminLoginTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            email='staff@example.com', name='Google Staff', password=None,
            signUp_by='google', is_verified=True, is_staff=True,
        )
        self.staff.user_permissions.add(Permission.objects.get(
            content_type__app_label='users', codename='view_user',
        ))

    def start(self, next_path='/admin/'):
        response = self.client.get('/admin/google/login/', {'next': next_path})
        self.assertEqual(response.status_code, 302)
        query = parse_qs(urlparse(response.url).query)
        self.assertEqual(urlparse(response.url).netloc, 'accounts.google.com')
        return query['state'][0]

    def callback(self, state, **extra):
        return self.client.get('/accounts/googleCallback', {'state': state, 'code': 'example-code', **extra})

    def mock_identity(self, post, get, email='staff@example.com', verified=True):
        post.return_value.json.return_value = {'access_token': 'example-google-token'}
        get.return_value.json.return_value = {'email': email, 'email_verified': verified, 'name': 'Google Staff'}

    def test_admin_login_has_google_button_and_existing_password_form(self):
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Continue with Google')
        self.assertContains(response, '/admin/google/login/')
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')

    def test_google_start_reuses_registered_callback_and_stores_expiring_state(self):
        response = self.client.get('/admin/google/login/')
        query = parse_qs(urlparse(response.url).query)
        self.assertEqual(query['redirect_uri'], ['http://testserver/accounts/googleCallback'])
        self.assertEqual(query['client_id'], ['example-client'])
        self.assertEqual(query['scope'], ['openid email profile'])
        self.assertTrue(query['state'][0].startswith('admin.'))
        self.assertEqual(self.client.session[SESSION_KEY]['state'], query['state'][0])
        self.assertNotIn('client_secret', query)
        self.assertIn('no-store', response['Cache-Control'])

    @patch('users.google.requests.get')
    @patch('users.google.requests.post')
    def test_google_staff_can_enter_admin_without_a_local_password(self, post, get):
        self.assertFalse(self.staff.has_usable_password())
        self.mock_identity(post, get)
        state = self.start('/admin/users/user/')
        original_session = self.client.session.session_key
        response = self.callback(state)
        self.assertRedirects(response, '/admin/users/user/', fetch_redirect_response=False)
        self.assertEqual(self.client.session[AUTH_SESSION_KEY], str(self.staff.pk))
        self.assertNotEqual(self.client.session.session_key, original_session)
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertEqual(self.client.get('/admin/').status_code, 200)
        self.assertEqual(self.client.get('/admin/users/user/').status_code, 200)
        self.assertEqual(response['Referrer-Policy'], 'no-referrer')
        self.assertEqual(post.call_args.kwargs['data']['redirect_uri'], 'http://testserver/accounts/googleCallback')
        self.staff.refresh_from_db()
        self.assertFalse(self.staff.is_superuser)
        self.assertFalse(self.staff.has_usable_password())

    @patch('users.google.requests.post')
    def test_invalid_state_is_rejected_before_google_exchange(self, post):
        self.start()
        response = self.callback('admin.invalid')
        self.assertEqual(response.status_code, 403)
        post.assert_not_called()
        self.assertNotIn(AUTH_SESSION_KEY, self.client.session)

    @patch('users.google.requests.post')
    def test_state_cannot_be_used_from_another_browser(self, post):
        state = self.start()
        response = Client().get('/accounts/googleCallback', {'state': state, 'code': 'example-code'})
        self.assertEqual(response.status_code, 403)
        post.assert_not_called()

    @patch('users.google.requests.post')
    def test_expired_state_is_rejected_before_exchange(self, post):
        state = self.start()
        session = self.client.session
        session[SESSION_KEY] = {**session[SESSION_KEY], 'issued_at': time.time() - STATE_MAX_AGE - 1}
        session.save()
        self.assertEqual(self.callback(state).status_code, 403)
        post.assert_not_called()

    @patch('users.google.requests.get')
    @patch('users.google.requests.post')
    def test_successful_state_cannot_be_replayed(self, post, get):
        self.mock_identity(post, get)
        state = self.start()
        self.assertEqual(self.callback(state).status_code, 302)
        self.assertEqual(self.callback(state).status_code, 403)
        self.assertEqual(post.call_count, 1)

    @patch('users.google.requests.get')
    @patch('users.google.requests.post')
    def test_nonstaff_is_denied_without_permission_changes(self, post, get):
        member = User.objects.create_user(
            email='member@example.com', name='Member', password=None,
            signUp_by='google', is_verified=True,
        )
        self.mock_identity(post, get, email=member.email)
        response = self.callback(self.start())
        self.assertEqual(response.status_code, 403)
        self.assertNotIn(AUTH_SESSION_KEY, self.client.session)
        member.refresh_from_db()
        self.assertFalse(member.is_staff)
        self.assertFalse(member.is_superuser)

    @patch('users.google.requests.get')
    @patch('users.google.requests.post')
    def test_unknown_google_account_is_not_created_by_admin_login(self, post, get):
        self.mock_identity(post, get, email='unknown@example.com')
        count = User.objects.count()
        self.assertEqual(self.callback(self.start()).status_code, 403)
        self.assertEqual(User.objects.count(), count)

    @patch('users.google.requests.get')
    @patch('users.google.requests.post')
    def test_unverified_google_email_is_denied(self, post, get):
        self.mock_identity(post, get, verified=False)
        self.assertEqual(self.callback(self.start()).status_code, 400)
        self.assertNotIn(AUTH_SESSION_KEY, self.client.session)

    @patch('users.google.requests.get')
    @patch('users.google.requests.post')
    def test_unverified_local_staff_account_is_denied(self, post, get):
        self.staff.is_verified = False
        self.staff.save(update_fields=['is_verified'])
        self.mock_identity(post, get)
        self.assertEqual(self.callback(self.start()).status_code, 403)
        self.assertNotIn(AUTH_SESSION_KEY, self.client.session)

    def test_external_and_nonadmin_redirects_are_not_accepted(self):
        for target in ['https://other.example/', '//other.example/', '/accounts/profile/']:
            with self.subTest(target=target):
                self.start(target)
                self.assertEqual(self.client.session[SESSION_KEY]['next'], '/admin/')

    @patch('users.google.requests.post')
    def test_google_cancellation_does_not_authenticate(self, post):
        response = self.callback(self.start(), error='access_denied')
        self.assertEqual(response.status_code, 400)
        self.assertNotIn(AUTH_SESSION_KEY, self.client.session)
        post.assert_not_called()

    @patch('users.google.requests.post', side_effect=requests.RequestException('example failure'))
    def test_provider_failure_shows_a_retry_page(self, post):
        response = self.callback(self.start())
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Back to admin login', status_code=400)
        self.assertNotIn(AUTH_SESSION_KEY, self.client.session)

    @patch('users.admin_google.serve_next_frontend', return_value=HttpResponse('React callback'))
    def test_regular_website_google_callback_still_goes_to_react(self, frontend):
        response = self.client.get('/accounts/googleCallback/', {'state': 'website-state', 'code': 'example-code'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'React callback')
        frontend.assert_called_once()

    @patch.dict(os.environ, {'GOOGLE_CLIENT_ID': '', 'GOOGLE_CLIENT_SECRET': ''})
    def test_unconfigured_google_button_is_hidden(self):
        self.assertNotContains(self.client.get('/admin/login/'), 'Continue with Google')
        self.assertEqual(self.client.get('/admin/google/login/').status_code, 503)

    def test_alternate_local_host_redirects_to_the_configured_callback_host(self):
        response = self.client.get('/admin/google/login/', HTTP_HOST='127.0.0.1')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.url).netloc, 'testserver')
        self.assertEqual(urlparse(response.url).path, '/admin/google/login/')
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_existing_admin_password_login_still_works(self):
        staff = User.objects.create_superuser('password@example.com', 'Password Staff', 'Password-horse-729!')
        response = self.client.post('/admin/login/', {'username': staff.email, 'password': 'Password-horse-729!', 'next': '/admin/'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session[AUTH_SESSION_KEY], str(staff.pk))
