from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import UserProfileSerializer, UpdateNameSerializer
from .models import Profile
from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            # Older accounts may not have a separate profile. Serialize an
            # unsaved instance to expose account details without writing on GET.
            profile = Profile(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)


class UpdateNameView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def patch(self, request):
        serializer = UpdateNameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_user_model().objects.select_for_update().get(pk=request.user.pk)
        user.first_name = serializer.validated_data['first_name']
        user.last_name = serializer.validated_data['last_name']
        user.name = ' '.join(filter(None, [user.first_name, user.last_name]))
        user.save(update_fields=['first_name', 'last_name', 'name'])
        profile = Profile.objects.filter(user=user).first() or Profile(user=user)
        profile.user = user
        response = Response(UserProfileSerializer(profile).data)
        response['Cache-Control'] = 'private, no-store'
        return response


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not isinstance(old_password, str) or not isinstance(new_password, str) or not new_password:
            return Response({'detail': 'Current and new passwords are required'}, status=400)
        if not user.check_password(old_password):
            return Response({'detail': 'Old password is incorrect'}, status=400)
        try:
            validate_password(new_password, user)
        except ValidationError as exc:
            return Response({'detail': ' '.join(exc.messages)}, status=400)
        user.set_password(new_password)
        user.save(update_fields=['password'])
        return Response({'detail': 'Password changed successfully'}, status=200)
