"""Expiring, purpose-bound account actions invalidated by account state changes."""

from django.conf import settings
from django.core import signing
from django.utils.crypto import constant_time_compare, salted_hmac

from .models import User


def account_state(user):
    return salted_hmac(
        'account-action-state', f'{user.pk}:{user.email}:{user.password}:{user.is_verified}',
    ).hexdigest()


def action_token(user, purpose):
    return signing.dumps({'uid': user.pk, 'state': account_state(user)}, salt=f'account.{purpose}')


def action_user(token, purpose):
    if not isinstance(token, str) or not token:
        raise signing.BadSignature('Token is required')
    data = signing.loads(token, salt=f'account.{purpose}', max_age=settings.ACCOUNT_ACTION_TOKEN_MAX_AGE)
    user = User.objects.get(pk=data['uid'])
    if not constant_time_compare(data['state'], account_state(user)):
        raise signing.BadSignature('Account state changed')
    return user
