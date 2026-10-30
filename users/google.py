"""Google's server-side code exchange shared by website and admin login."""

import os

import requests
from django.conf import settings


def google_configured():
    return bool(os.environ.get('GOOGLE_CLIENT_ID') and os.environ.get('GOOGLE_CLIENT_SECRET'))


def google_redirect_uri():
    path = os.environ.get('GOOGLE_REDIRECT_URI', 'accounts/googleCallback').lstrip('/')
    return f'{settings.FRONTEND_BASE_URL}/{path}'


def verified_google_identity(code):
    tokens = requests.post('https://oauth2.googleapis.com/token', data={
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': google_redirect_uri(),
    }, timeout=15)
    tokens.raise_for_status()
    info = requests.get('https://www.googleapis.com/oauth2/v3/userinfo', headers={
        'Authorization': f"Bearer {tokens.json()['access_token']}",
    }, timeout=15)
    info.raise_for_status()
    data = info.json()
    if not isinstance(data, dict) or data.get('email_verified') is not True or not isinstance(data.get('email'), str) or not data['email']:
        raise ValueError('A verified Google email is required')
    return data
