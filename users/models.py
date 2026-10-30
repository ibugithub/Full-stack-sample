from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
  def create_user(self, email, name, password=None, signUp_by='email', **extra_fields):
    if not email:
        raise ValueError('Users must have an email address')
    parts = name.strip().split(maxsplit=1)
    extra_fields.setdefault('first_name', parts[0] if parts else '')
    extra_fields.setdefault('last_name', parts[1] if len(parts) > 1 else '')
    user = self.model(email=self.normalize_email(email), name=name, signUp_by=signUp_by, **extra_fields)
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_superuser(self, email, name, password, **extra_fields):
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_verified', True)
    extra_fields.setdefault('is_superuser', True)
    if extra_fields.get('is_staff') is not True:
        raise ValueError('Superusers must have is_staff=True.')
    if extra_fields.get('is_superuser') is not True:
        raise ValueError('Superusers must have is_superuser=True.')
    return self.create_user(email, name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
  SIGNUP_METHODS = [
    ('email', 'Email'),
    ('google', 'Google'),
    ('facebook', 'Facebook'),
    ('microsoft', 'Microsoft'),
  ]
  email = models.EmailField(unique=True)
  name = models.CharField(max_length=255)
  first_name = models.CharField(max_length=255, blank=True, default='')
  last_name = models.CharField(max_length=255, blank=True, default='')
  signUp_by = models.CharField(max_length=20, choices=SIGNUP_METHODS, default='email')
  is_verified = models.BooleanField(default=False)
  is_staff = models.BooleanField(default=False, help_text='Allows this user to sign in to the admin dashboard. Groups and permissions control access to features.')
  is_superuser = models.BooleanField(default=False)
  objects = UserManager()

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['name']

  def __str__(self):
    return self.email


class CustomPermissionGroup(models.Model):
  owner = models.OneToOneField(
    User, on_delete=models.SET_NULL, null=True, blank=True,
    related_name='custom_permission_bundle',
  )
  group = models.OneToOneField(
    'auth.Group', on_delete=models.CASCADE, related_name='custom_permission_bundle',
  )
