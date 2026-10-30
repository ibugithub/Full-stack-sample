from django.contrib.auth import authenticate, password_validation
from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import serializers

from .models import User


class AccountSerializer(serializers.ModelSerializer):
    signup_method = serializers.CharField(source='signUp_by', read_only=True)
    admin_url = serializers.SerializerMethodField()

    def get_admin_url(self, user):
        return reverse('admin:index') if user.is_staff and user.is_active else None

    class Meta:
        model = User
        fields = ['email', 'name', 'first_name', 'last_name', 'signup_method', 'is_staff', 'admin_url']
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password2 = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ['email', 'name', 'first_name', 'last_name', 'password', 'password2']
        read_only_fields = ['first_name', 'last_name']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('Passwords do not match')
        try:
            password_validation.validate_password(data['password'], User(email=data['email'], name=data['name']))
        except ValidationError as exc:
            raise serializers.ValidationError({'password': exc.messages})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)


class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, data):
        user = authenticate(request=self.context.get('request'), email=data['email'], password=data['password'])
        if user is None:
            raise serializers.ValidationError('Invalid credentials')
        data['user'] = user
        return data


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'is_staff']
