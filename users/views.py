from urllib.parse import urlencode
import os
import secrets

import requests
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core import signing
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenBlacklistView

from userProfile.models import Profile
from users.utils.sendEmail import send_email
from .models import User
from .serializers import AccountSerializer, ListUserSerializer, SignInSerializer, UserSerializer
from .tokens import action_token, action_user
from .google import verified_google_identity
from .throttles import (
    LoginThrottle, SignupThrottle, PasswordResetThrottle, PasswordResetEmailThrottle,
    VerificationResendThrottle, VerificationResendEmailThrottle,
    PasswordResetConfirmThrottle, EmailVerifyThrottle,
)


def send_account_action(user, purpose):
    page = 'verifyEmail' if purpose == 'verify' else 'resetPassword'
    url = f"{settings.FRONTEND_BASE_URL}/accounts/{page}?{urlencode({'token': action_token(user, purpose)})}"
    subject = 'Verify your email' if purpose == 'verify' else 'Reset your password'
    send_email(subject=subject, recipient_list=[user.email], message=f'{subject}: {url}')


class CreateUser(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [SignupThrottle]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Roll back account creation if delivery fails, so registration can be retried.
        with transaction.atomic():
            user = serializer.save()
            Profile.objects.create(user=user)
            send_account_action(user, 'verify')
        return Response(AccountSerializer(user).data, status=201)


class SignInView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LoginThrottle]

    def post(self, request):
        serializer = SignInSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if not user.is_verified:
            return Response({'detail': 'Please verify your email before signing in', 'code': 'email_unverified'}, status=403)
        return token_response(user)


class ListUserView(generics.ListAPIView):
    queryset = User.objects.all().order_by('id')
    serializer_class = ListUserSerializer
    permission_classes = [permissions.IsAdminUser]


class ValidateTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return Response(AccountSerializer(request.user).data)


class LogoutView(TokenBlacklistView):
    """Revoke the supplied refresh token, even when its access token has expired."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.data = {'detail': 'Refresh token revoked.'}
        response['Cache-Control'] = 'no-store'
        return response


def token_response(user):
    refresh = RefreshToken.for_user(user)
    return Response({'refresh': str(refresh), 'access': str(refresh.access_token)})


def social_account(data, provider):
    email = data.get('email')
    name = data.get('name') or email
    if not email:
        return Response({'detail': 'The provider did not supply an email address'}, status=400)
    with transaction.atomic():
        user = User.objects.filter(email__iexact=email).first()
        if user and not user.is_verified:
            return Response({'detail': 'Verify the existing account email before using social sign-in'}, status=403)
        if user is None:
            user = User.objects.create_user(email=email, name=name, password=secrets.token_urlsafe(32), signUp_by=provider, is_verified=True)
            Profile.objects.create(user=user)
    return token_response(user)


def provider_credentials(client_key, secret_key):
    client, secret = os.environ.get(client_key), os.environ.get(secret_key)
    return (client, secret) if client and secret else None


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([LoginThrottle])
def GetGoogleUserInfo(request):
    code = request.data.get('code')
    if not code:
        return Response({'detail': 'Authorization code is required'}, status=400)
    credentials = provider_credentials('GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET')
    if credentials is None:
        return Response({'detail': 'Google sign-in is not configured'}, status=503)
    try:
        data = verified_google_identity(code)
        return social_account(data, 'google')
    except (requests.RequestException, ValueError, KeyError):
        return Response({'detail': 'Google sign-in could not be completed'}, status=400)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([LoginThrottle])
def GetFBUserInfo(request):
    code = request.data.get('code')
    if not code:
        return Response({'detail': 'Authorization code is required'}, status=400)
    credentials = provider_credentials('FACEBOOK_APP_ID', 'FACEBOOK_APP_SECRET')
    if credentials is None:
        return Response({'detail': 'Facebook sign-in is not configured'}, status=503)
    try:
        tokens = requests.get('https://graph.facebook.com/oauth/access_token', params={
            'client_id': credentials[0], 'client_secret': credentials[1], 'code': code,
            'redirect_uri': f"{settings.FRONTEND_BASE_URL}/{os.environ.get('FACEBOOK_REDIRECT_URI', 'accounts/fbCallback')}",
        }, timeout=15)
        tokens.raise_for_status()
        info = requests.get('https://graph.facebook.com/me', params={
            'fields': 'id,name,email', 'access_token': tokens.json()['access_token'],
        }, timeout=15)
        info.raise_for_status()
        return social_account(info.json(), 'facebook')
    except (requests.RequestException, ValueError, KeyError):
        return Response({'detail': 'Facebook sign-in could not be completed'}, status=400)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([LoginThrottle])
def GetMsUserInfo(request):
    code = request.data.get('code')
    if not code:
        return Response({'detail': 'Authorization code is required'}, status=400)
    credentials = provider_credentials('MICROSOFT_CLIENT_ID', 'MICROSOFT_CLIENT_SECRET')
    if credentials is None:
        return Response({'detail': 'Microsoft sign-in is not configured'}, status=503)
    try:
        tokens = requests.post('https://login.microsoftonline.com/common/oauth2/v2.0/token', data={
            'client_id': credentials[0], 'client_secret': credentials[1], 'code': code,
            'grant_type': 'authorization_code', 'scope': 'User.Read openid profile email',
            'redirect_uri': f"{settings.FRONTEND_BASE_URL}/{os.environ.get('MICROSOFT_REDIRECT_URI', 'accounts/msCallback')}",
        }, timeout=15)
        tokens.raise_for_status()
        info = requests.get('https://graph.microsoft.com/v1.0/me', headers={
            'Authorization': f"Bearer {tokens.json()['access_token']}",
        }, timeout=15)
        info.raise_for_status()
        data = info.json()
        return social_account({'email': data.get('mail') or data.get('userPrincipalName'), 'name': data.get('displayName')}, 'microsoft')
    except (requests.RequestException, ValueError, KeyError):
        return Response({'detail': 'Microsoft sign-in could not be completed'}, status=400)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([EmailVerifyThrottle])
def verifyEmail(request):
    try:
        with transaction.atomic():
            user = action_user(request.data.get('token', ''), 'verify')
            user = User.objects.select_for_update().get(pk=user.pk)
            # Check again after locking to prevent concurrent token reuse.
            action_user(request.data.get('token', ''), 'verify')
            user.is_verified = True
            user.save(update_fields=['is_verified'])
        return Response({'detail': 'Email verified successfully'})
    except (signing.BadSignature, User.DoesNotExist, KeyError, TypeError):
        return Response({'detail': 'Invalid or expired verification link'}, status=400)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([VerificationResendThrottle, VerificationResendEmailThrottle])
def reSendVerificationEmail(request):
    email = request.data.get('email')
    if not email:
        return Response({'detail': 'Email is required'}, status=400)
    user = User.objects.filter(email=email, is_verified=False).first()
    if user:
        send_account_action(user, 'verify')
    return Response({'detail': 'If the account needs verification, an email has been sent'})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([PasswordResetThrottle, PasswordResetEmailThrottle])
def forgetPassword(request):
    email = request.data.get('email')
    if not email:
        return Response({'detail': 'Email is required'}, status=400)
    user = User.objects.filter(email=email).first()
    if user:
        send_account_action(user, 'reset')
    return Response({'detail': 'If the account exists, a password reset email has been sent'})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([PasswordResetConfirmThrottle])
def resetPassword(request):
    token, password = request.data.get('token', ''), request.data.get('password')
    if not isinstance(password, str) or not password:
        return Response({'detail': 'Password is required'}, status=400)
    try:
        with transaction.atomic():
            user = action_user(token, 'reset')
            user = User.objects.select_for_update().get(pk=user.pk)
            action_user(token, 'reset')
            validate_password(password, user)
            user.set_password(password)
            user.save(update_fields=['password'])
        return Response({'detail': 'Password reset successfully'})
    except ValidationError as exc:
        return Response({'detail': ' '.join(exc.messages)}, status=400)
    except (signing.BadSignature, User.DoesNotExist, KeyError, TypeError):
        return Response({'detail': 'Invalid or expired password reset link'}, status=400)
