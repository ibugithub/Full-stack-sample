from datetime import timedelta

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


class LogoutTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.user = User.objects.create_user(
            email='logout@example.com', name='Logout Member',
            password='Logout-horse-729!', is_verified=True,
        )
        self.token = RefreshToken.for_user(self.user)

    def test_logout_prevents_refresh_without_requiring_an_access_token(self):
        refresh = str(self.token)
        self.assertEqual(self.api.post('/api/users/refresh/', {'refresh': refresh}).status_code, 200)
        response = self.api.post('/api/users/logout/', {'refresh': refresh})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'detail': 'Refresh token revoked.'})
        self.assertEqual(response['Cache-Control'], 'no-store')
        self.assertTrue(BlacklistedToken.objects.filter(token__jti=self.token['jti']).exists())
        response = self.api.post('/api/users/refresh/', {'refresh': refresh})
        self.assertEqual(response.status_code, 401)
        self.assertIn('detail', response.data)

    def test_an_invalid_access_header_does_not_prevent_revocation(self):
        self.api.credentials(HTTP_AUTHORIZATION='Bearer expired-or-invalid')
        response = self.api.post('/api/users/logout/', {'refresh': str(self.token)})
        self.assertEqual(response.status_code, 200)

    def test_other_sessions_are_not_revoked(self):
        other = RefreshToken.for_user(self.user)
        self.api.post('/api/users/logout/', {'refresh': str(self.token)})
        self.assertEqual(self.api.post('/api/users/refresh/', {'refresh': str(other)}).status_code, 200)

    def test_existing_access_token_keeps_its_original_expiration(self):
        access = str(self.token.access_token)
        self.api.post('/api/users/logout/', {'refresh': str(self.token)})
        self.api.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        self.assertEqual(self.api.post('/api/users/validateUser/').status_code, 200)

    def test_missing_refresh_returns_field_validation_errors(self):
        response = self.api.post('/api/users/logout/', {})
        self.assertEqual(response.status_code, 400)
        self.assertIn('refresh', response.data['errors'])

    def test_invalid_access_and_expired_tokens_are_rejected(self):
        expired = RefreshToken.for_user(self.user)
        expired.set_exp(lifetime=timedelta(seconds=-1))
        for token in ['invalid', str(self.token.access_token), str(expired)]:
            with self.subTest(token_type='invalid/expired'):
                response = self.api.post('/api/users/logout/', {'refresh': token})
                self.assertEqual(response.status_code, 401)
                self.assertIn('detail', response.data)

    def test_repeated_logout_reports_the_token_is_already_invalid(self):
        refresh = str(self.token)
        self.assertEqual(self.api.post('/api/users/logout/', {'refresh': refresh}).status_code, 200)
        self.assertEqual(self.api.post('/api/users/logout/', {'refresh': refresh}).status_code, 401)

    def test_tokens_issued_before_blacklist_tracking_can_be_revoked(self):
        refresh = str(self.token)
        OutstandingToken.objects.filter(jti=self.token['jti']).delete()
        self.assertEqual(self.api.post('/api/users/logout/', {'refresh': refresh}).status_code, 200)
        self.assertEqual(self.api.post('/api/users/refresh/', {'refresh': refresh}).status_code, 401)
