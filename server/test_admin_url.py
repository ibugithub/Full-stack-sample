"""Exercise the admin and OAuth flow mounted at a custom address."""
from unittest.mock import patch

from django.contrib import admin
from django.test import TestCase, override_settings
from django.urls import path, reverse
from rest_framework.test import APIClient

from server.urls import urlpatterns as application_patterns
from users.admin_google import SESSION_KEY
from users.models import User

urlpatterns = [path('private-office/', admin.site.urls), *application_patterns[1:]]


@override_settings(ROOT_URLCONF=__name__, FRONTEND_BASE_URL='http://testserver')
class CustomAdminURLTests(TestCase):
    def test_custom_login_and_password_auth(self):
        staff = User.objects.create_user(
            email='staff@example.com', name='Staff', password='Strong-example-729!',
            is_staff=True, is_verified=True,
        )
        self.assertEqual(reverse('admin:index'), '/private-office/')
        self.assertEqual(self.client.get('/private-office/login/').status_code, 200)
        response = self.client.post('/private-office/login/', {
            'username': staff.email, 'password': 'Strong-example-729!', 'next': reverse('admin:index'),
        })
        self.assertRedirects(response, '/private-office/')
        self.assertNotEqual(self.client.get('/admin/login/').status_code, 200)

    def test_account_url_is_only_provided_to_staff(self):
        user = User.objects.create_user(email='user@example.com', name='User', is_verified=True)
        api = APIClient()
        api.force_authenticate(user)
        self.assertIsNone(api.post('/api/users/validateUser/').data['admin_url'])
        user.is_staff = True
        user.save(update_fields=['is_staff'])
        self.assertEqual(api.post('/api/users/validateUser/').data['admin_url'], '/private-office/')

    @patch.dict('os.environ', {'GOOGLE_CLIENT_ID': 'client', 'GOOGLE_CLIENT_SECRET': 'secret'})
    @patch('users.admin_google.verified_google_identity')
    def test_google_login_returns_to_custom_admin(self, identity):
        User.objects.create_user(
            email='staff@example.com', name='Staff', is_staff=True, is_verified=True,
        )
        identity.return_value = {'email': 'staff@example.com'}
        response = self.client.get(reverse('admin:google-login'), {'next': '/admin/'})
        self.assertEqual(response.status_code, 302)
        pending = self.client.session[SESSION_KEY]
        self.assertEqual(pending['next'], '/private-office/')
        response = self.client.get(reverse('google-oauth-callback'), {
            'state': pending['state'], 'code': 'code',
        })
        self.assertRedirects(response, '/private-office/')
