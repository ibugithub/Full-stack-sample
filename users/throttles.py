"""Endpoint-specific account limits shared through a dedicated cache."""

from collections.abc import Mapping

from django.core.cache import caches
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.crypto import salted_hmac
from rest_framework.settings import api_settings
from rest_framework.throttling import SimpleRateThrottle


class AccountIPThrottle(SimpleRateThrottle):
    @property
    def cache(self):
        return caches['auth_throttles']

    def get_rate(self):
        return api_settings.DEFAULT_THROTTLE_RATES[self.scope]

    def get_cache_key(self, request, view):
        identity = self.get_ident(request) or 'unknown'
        digest = salted_hmac('account-ip-rate-limit', identity).hexdigest()
        return self.cache_format % {'scope': self.scope, 'ident': digest}


class AccountEmailThrottle(AccountIPThrottle):
    def get_cache_key(self, request, view):
        if not isinstance(request.data, Mapping):
            return None
        email = request.data.get('email')
        if not isinstance(email, str):
            return None
        email = email.strip().lower()
        try:
            validate_email(email)
        except ValidationError:
            return None
        # Do not store raw email addresses in cache keys or check account existence.
        digest = salted_hmac('account-email-rate-limit', email).hexdigest()
        return self.cache_format % {'scope': self.scope, 'ident': digest}


class LoginThrottle(AccountIPThrottle):
    scope = 'auth_login'


class SignupThrottle(AccountIPThrottle):
    scope = 'auth_signup'


class PasswordResetThrottle(AccountIPThrottle):
    scope = 'auth_password_reset'


class PasswordResetEmailThrottle(AccountEmailThrottle):
    scope = 'auth_password_reset_email'


class VerificationResendThrottle(AccountIPThrottle):
    scope = 'auth_verification_resend'


class VerificationResendEmailThrottle(AccountEmailThrottle):
    scope = 'auth_verification_resend_email'


class PasswordResetConfirmThrottle(AccountIPThrottle):
    scope = 'auth_reset_confirm'


class EmailVerifyThrottle(AccountIPThrottle):
    scope = 'auth_email_verify'
