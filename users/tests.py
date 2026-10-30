import tempfile
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from django.apps import apps
from django.contrib.auth.models import Permission
from django.core import mail
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from userProfile.models import Profile
from .models import User
from .tokens import action_token


class AccountTemplateTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.user = User.objects.create_user(
            email='member@example.com', name='Sample Member', password='Correct-horse-729!', is_verified=True,
        )
        Profile.objects.create(user=self.user)

    def authenticate(self, user=None):
        access = RefreshToken.for_user(user or self.user).access_token
        self.api.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

    def test_signup_verification_signin_and_refresh(self):
        response = self.api.post('/api/users/create/', {
            'email': 'new@example.com', 'name': 'New Member',
            'password': 'Strong-example-729!', 'password2': 'Strong-example-729!',
        })
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(len(mail.outbox), 1)
        url = mail.outbox[0].body.split()[-1]
        token = parse_qs(urlparse(url).query)['token'][0]
        credentials = {'email': 'new@example.com', 'password': 'Strong-example-729!'}
        self.assertEqual(self.api.post('/api/users/signin/', credentials).status_code, 403)
        self.assertEqual(self.api.post('/api/users/verifyEmail/', {'token': token}).status_code, 200)
        self.assertEqual(self.api.post('/api/users/verifyEmail/', {'token': token}).status_code, 400)
        response = self.api.post('/api/users/signin/', credentials)
        self.assertEqual(response.status_code, 200)
        refreshed = self.api.post('/api/users/refresh/', {'refresh': response.data['refresh']})
        self.assertEqual(refreshed.status_code, 200)
        self.assertIn('access', refreshed.data)

    @patch('users.views.send_email', side_effect=RuntimeError('Mail unavailable'))
    def test_failed_signup_delivery_does_not_leave_an_unusable_account(self, send_email):
        with self.assertRaises(RuntimeError):
            self.api.post('/api/users/create/', {
                'email': 'failed@example.com', 'name': 'Failed Member',
                'password': 'Strong-example-729!', 'password2': 'Strong-example-729!',
            })
        self.assertFalse(User.objects.filter(email='failed@example.com').exists())

    def test_password_validation_rejects_weak_signup(self):
        response = self.api.post('/api/users/create/', {
            'email': 'weak@example.com', 'name': 'Weak Member', 'password': '123', 'password2': '123',
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(email='weak@example.com').exists())

    def test_profile_name_and_password_changes(self):
        self.assertEqual(self.api.get('/api/profile/getProfile/').status_code, 401)
        self.authenticate()
        response = self.api.post('/api/users/validateUser/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['signup_method'], 'email')
        self.assertEqual(self.api.get('/api/profile/getProfile/').status_code, 200)
        response = self.api.patch('/api/profile/updateName/', {'first_name': 'Updated', 'last_name': 'Member'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['name'], 'Updated Member')
        response = self.api.post('/api/profile/changePassword/', {'old_password': 'Correct-horse-729!', 'new_password': '123'})
        self.assertEqual(response.status_code, 400)
        response = self.api.post('/api/profile/changePassword/', {'old_password': 'Correct-horse-729!', 'new_password': 'Changed-horse-729!'})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Changed-horse-729!'))

    def test_account_reports_current_staff_status(self):
        self.authenticate()
        self.assertIs(self.api.post('/api/users/validateUser/').data['is_staff'], False)
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])
        self.assertIs(self.api.post('/api/users/validateUser/').data['is_staff'], True)
        self.user.is_staff = False
        self.user.save(update_fields=['is_staff'])
        self.assertIs(self.api.post('/api/users/validateUser/').data['is_staff'], False)

    def test_password_reset_is_purpose_bound_and_single_use(self):
        password = 'Replacement-horse-729!'
        access = str(RefreshToken.for_user(self.user).access_token)
        self.assertEqual(self.api.post('/api/users/resetPassword/', {'token': access, 'password': password}).status_code, 400)
        verification = action_token(self.user, 'verify')
        self.assertEqual(self.api.post('/api/users/resetPassword/', {'token': verification, 'password': password}).status_code, 400)
        token = action_token(self.user, 'reset')
        self.assertEqual(self.api.post('/api/users/resetPassword/', {'token': token, 'password': password}).status_code, 200)
        self.assertEqual(self.api.post('/api/users/resetPassword/', {'token': token, 'password': password}).status_code, 400)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(password))

    @override_settings(ACCOUNT_ACTION_TOKEN_MAX_AGE=-1)
    def test_expired_action_links_are_rejected(self):
        token = action_token(self.user, 'reset')
        response = self.api.post('/api/users/resetPassword/', {'token': token, 'password': 'Replacement-horse-729!'})
        self.assertEqual(response.status_code, 400)

    def test_password_reset_email_does_not_enumerate_accounts(self):
        existing = self.api.post('/api/users/forgetPassword/', {'email': self.user.email})
        missing = self.api.post('/api/users/forgetPassword/', {'email': 'missing@example.com'})
        self.assertEqual(existing.data, missing.data)
        self.assertEqual(len(mail.outbox), 1)

    def test_user_listing_is_staff_only(self):
        self.authenticate()
        self.assertEqual(self.api.get('/api/users/list/').status_code, 403)
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])
        self.assertEqual(self.api.get('/api/users/list/').status_code, 200)

    def test_missing_password_input_is_a_validation_error(self):
        self.authenticate()
        self.assertEqual(self.api.post('/api/profile/changePassword/', {}).status_code, 400)

    def test_admin_dashboard_and_generic_counts(self):
        admin = User.objects.create_superuser('admin@example.com', 'Admin Member', 'Correct-horse-729!')
        self.client.force_login(admin)
        for url in ['/admin/', '/admin/accounts/', '/admin/users/user/', f'/admin/users/user/{self.user.pk}/change/', '/admin/auth/group/', '/admin/users/user/add/']:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, url)
            self.assertNotContains(response, 'notification-feed')
        response = self.client.get(reverse('admin:dashboard-counts'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('/admin/users/user/', response.json()['counts'])
        self.assertIn('private', response['Cache-Control'])
        self.assertIn('no-store', response['Cache-Control'])

    def test_counts_respect_staff_permissions(self):
        staff = User.objects.create_user('staff@example.com', 'Staff Member', 'Correct-horse-729!', is_staff=True)
        self.client.force_login(staff)
        self.assertEqual(self.client.get(reverse('admin:dashboard-counts')).json()['counts'], {})
        staff.user_permissions.add(Permission.objects.get(codename='view_user', content_type__app_label='users'))
        response = self.client.get(reverse('admin:dashboard-counts'))
        self.assertEqual(set(response.json()['counts']), {'/admin/users/user/'})

    def test_removed_apps_and_routes_are_absent(self):
        for label in ['catalog', 'orders', 'service_requests', 'notifications']:
            self.assertFalse(apps.is_installed(label))
        for path in ['/api/catalog/products/', '/api/cart/', '/api/orders/', '/api/service-requests/', '/api/profile/addresses/']:
            self.assertEqual(self.api.get(path).status_code, 404, path)

    @patch.dict('os.environ', {'GOOGLE_CLIENT_ID': '', 'GOOGLE_CLIENT_SECRET': ''})
    def test_unconfigured_social_provider_is_optional(self):
        self.assertEqual(self.api.post('/api/users/getGoogleUsrInfo/', {'code': 'example'}).status_code, 503)

    @patch('users.views.requests.get')
    @patch('users.views.requests.post')
    @patch.dict('os.environ', {'GOOGLE_CLIENT_ID': 'example', 'GOOGLE_CLIENT_SECRET': 'example'})
    def test_configured_social_login_creates_verified_account(self, post, get):
        post.return_value.json.return_value = {'access_token': 'provider-token'}
        get.return_value.json.return_value = {'email': 'social@example.com', 'name': 'Social Member', 'email_verified': True}
        response = self.api.post('/api/users/getGoogleUsrInfo/', {'code': 'example'})
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(email='social@example.com')
        self.assertTrue(user.is_verified)
        self.assertEqual(user.signUp_by, 'google')
        self.assertTrue(Profile.objects.filter(user=user).exists())


class CombinedFrontendTests(SimpleTestCase):
    def test_exported_pages_assets_and_missing_routes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'index.html').write_text('Template homepage', encoding='utf-8')
            (root / '404.html').write_text('Page not found', encoding='utf-8')
            (root / 'accounts' / 'signin').mkdir(parents=True)
            (root / 'accounts' / 'signin' / 'index.html').write_text('Sign in', encoding='utf-8')
            (root / 'asset.js').write_text('window.template = true;', encoding='utf-8')
            with override_settings(FRONTEND_BUILD_DIR=root):
                for url, expected in [('/', b'Template homepage'), ('/accounts/signin/', b'Sign in'), ('/asset.js', b'window.template = true;')]:
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(b''.join(response.streaming_content), expected)
                response = self.client.get('/ready-stock/')
                self.assertEqual(response.status_code, 404)
                self.assertEqual(b''.join(response.streaming_content), b'Page not found')
                self.assertEqual(self.client.get('/../outside.txt').status_code, 404)

    def test_missing_build_returns_404(self):
        with override_settings(FRONTEND_BUILD_DIR=Path('/missing-template-build')):
            self.assertEqual(self.client.get('/').status_code, 404)
