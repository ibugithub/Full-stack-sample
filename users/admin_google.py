"""Google sign-in for existing staff accounts using Django's admin session."""

from math import ceil
import os
import secrets
import time
from urllib.parse import urlencode, urlsplit, urlunsplit

import requests
from django.contrib import admin
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.crypto import constant_time_compare
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from server.frontend import serve_next_frontend
from .google import google_configured, google_redirect_uri, verified_google_identity
from .models import User
from .throttles import LoginThrottle

SESSION_KEY = 'admin_google_oauth'
STATE_PREFIX = 'admin.'
STATE_MAX_AGE = 300


def safe_admin_next(request, target):
    root = reverse('admin:index')
    if isinstance(target, str) and target.startswith(root) and url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure(),
    ):
        return target
    return root


def admin_google_error(request, detail, status=400, wait=None):
    response = render(request, 'admin/google_login_error.html', {
        **admin.site.each_context(request),
        'title': 'Google sign-in',
        'detail': detail,
    }, status=status)
    response['Referrer-Policy'] = 'no-referrer'
    if wait is not None:
        response['Retry-After'] = str(wait)
    return response


def login_limit_response(request):
    throttle = LoginThrottle()
    if throttle.allow_request(request, None):
        return None
    wait = ceil(throttle.wait() or 60)
    return admin_google_error(request, f'Too many sign-in attempts. Please try again in {wait} seconds.', status=429, wait=wait)


@never_cache
@require_GET
def google_admin_login(request):
    if not google_configured():
        return admin_google_error(request, 'Google sign-in is not configured.', status=503)
    target = safe_admin_next(request, request.GET.get('next'))
    callback = urlsplit(google_redirect_uri())
    # The OAuth state cookie must belong to the same host as the callback.
    # This also handles opening local admin through 127.0.0.1 instead of localhost.
    if callback.netloc.lower() != request.get_host().lower():
        response = HttpResponseRedirect(urlunsplit((
            callback.scheme, callback.netloc, reverse('admin:google-login'),
            urlencode({'next': target}), '',
        )))
        response['Referrer-Policy'] = 'no-referrer'
        return response
    limited = login_limit_response(request)
    if limited is not None:
        return limited
    state = STATE_PREFIX + secrets.token_urlsafe(32)
    request.session[SESSION_KEY] = {'state': state, 'issued_at': time.time(), 'next': target}
    query = urlencode({
        'client_id': os.environ['GOOGLE_CLIENT_ID'],
        'redirect_uri': google_redirect_uri(),
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'prompt': 'select_account',
    })
    response = HttpResponseRedirect(f'https://accounts.google.com/o/oauth2/v2/auth?{query}')
    response['Referrer-Policy'] = 'no-referrer'
    return response


@never_cache
@require_GET
def google_callback(request):
    state = request.GET.get('state', '')
    if not state.startswith(STATE_PREFIX):
        # The ordinary website OAuth flow still finishes in React and returns JWTs.
        response = serve_next_frontend(request, path=request.path.lstrip('/'))
        response['Referrer-Policy'] = 'no-referrer'
        return response
    limited = login_limit_response(request)
    if limited is not None:
        return limited
    pending = request.session.get(SESSION_KEY)
    if not isinstance(pending, dict) or not constant_time_compare(state, pending.get('state', '')):
        return admin_google_error(request, 'This sign-in request is invalid. Return to admin login and try again.', status=403)
    del request.session[SESSION_KEY]
    age = time.time() - pending.get('issued_at', 0)
    if age < 0 or age > STATE_MAX_AGE:
        return admin_google_error(request, 'This sign-in request has expired. Please try again.', status=403)
    if request.GET.get('error') or not request.GET.get('code'):
        return admin_google_error(request, 'Google sign-in was not completed. Please try again.')
    if not google_configured():
        return admin_google_error(request, 'Google sign-in is not configured.', status=503)
    try:
        identity = verified_google_identity(request.GET['code'])
    except (requests.RequestException, ValueError, KeyError):
        return admin_google_error(request, 'Google could not verify this sign-in. Please try again.')
    user = User.objects.filter(email__iexact=identity['email']).first()
    if user is None or not user.is_verified or not user.is_active or not user.is_staff:
        return admin_google_error(request, 'This Google account does not have staff access. Contact your administrator.', status=403)
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    response = HttpResponseRedirect(safe_admin_next(request, pending.get('next')))
    response['Referrer-Policy'] = 'no-referrer'
    return response
