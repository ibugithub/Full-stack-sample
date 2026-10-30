from django.db import models
from users.models import User
from cloudinary.models import CloudinaryField
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Display_name = models.CharField(max_length=255, null=True, blank=True)
    profile_picture = CloudinaryField('profile_pictures', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email
