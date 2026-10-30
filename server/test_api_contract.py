from django.test import TestCase
from rest_framework.test import APIClient

from userProfile.models import Profile
from users.models import User


class AccountResponseContractTests(TestCase):
    def setUp(self):
        self.api = APIClient()
        self.password = 'Contract-horse-729!'
        self.user = User.objects.create_user(
            email='contract@example.com', name='Contract Member',
            password=self.password, is_verified=True,
        )
        Profile.objects.create(user=self.user, Display_name='Member')

    def login(self):
        response = self.api.post('/api/users/signin/', {
            'email': self.user.email, 'password': self.password,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data), {'access', 'refresh'})
        self.api.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        return response.data

    def test_login_and_refresh_use_the_same_token_names(self):
        tokens = self.login()
        response = self.api.post('/api/users/refresh/', {'refresh': tokens['refresh']})
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.api.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        self.assertEqual(self.api.get('/api/profile/getProfile/').status_code, 200)

    def test_account_and_profile_use_consistent_snake_case_fields(self):
        self.login()
        account = self.api.post('/api/users/validateUser/').data
        profile = self.api.get('/api/profile/getProfile/').data
        self.assertEqual(account['signup_method'], 'email')
        self.assertNotIn('signUp_by', account)
        self.assertEqual(profile['user'], account)
        self.assertEqual(profile['display_name'], 'Member')
        self.assertNotIn('Display_name', profile)
        updated = self.api.patch('/api/profile/updateName/', {'first_name': 'Updated'})
        self.assertEqual(updated.status_code, 200)
        self.assertIn('display_name', updated.data)
        self.assertEqual(updated.data['user']['signup_method'], 'email')

    def test_signup_retains_all_field_validation_errors(self):
        response = self.api.post('/api/users/create/', {})
        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(response.data['detail'], str)
        self.assertEqual(response.data['code'], 'validation_error')
        self.assertTrue({'email', 'name', 'password', 'password2'}.issubset(response.data['errors']))

    def test_bad_credentials_keep_a_readable_detail_and_validation_map(self):
        response = self.api.post('/api/users/signin/', {
            'email': self.user.email, 'password': 'wrong-password',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], 'Invalid credentials')
        self.assertIn('non_field_errors', response.data['errors'])

    def test_framework_errors_share_the_detail_field(self):
        response = self.api.get('/api/profile/getProfile/')
        self.assertEqual(response.status_code, 401)
        self.assertIsInstance(response.data['detail'], str)
        self.assertIn('code', response.data)
        response = self.api.get('/api/users/signin/')
        self.assertEqual(response.status_code, 405)
        self.assertIsInstance(response.data['detail'], str)
        response = self.api.post('/api/users/signin/', data='{', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'parse_error')

    def test_explicit_account_errors_share_the_detail_field(self):
        for path in ['/api/users/forgetPassword/', '/api/users/resendVerification/', '/api/users/resetPassword/', '/api/users/getGoogleUsrInfo/']:
            with self.subTest(path=path):
                response = self.api.post(path, {})
                self.assertEqual(response.status_code, 400)
                self.assertIsInstance(response.data['detail'], str)
                self.assertNotIn('error', response.data)
                self.assertNotIn('message', response.data)
        self.login()
        response = self.api.post('/api/profile/changePassword/', {})
        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.data)

    def test_success_messages_use_detail(self):
        response = self.api.post('/api/users/forgetPassword/', {'email': 'missing@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data), {'detail'})

    def test_unverified_login_keeps_its_specific_error_code(self):
        self.user.is_verified = False
        self.user.save(update_fields=['is_verified'])
        response = self.api.post('/api/users/signin/', {
            'email': self.user.email, 'password': self.password,
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['code'], 'email_unverified')
        self.assertIn('detail', response.data)
