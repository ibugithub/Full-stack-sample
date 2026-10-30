from rest_framework import serializers
from .models import Profile
from users.serializers import AccountSerializer
import os
class UpdateNameSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255, allow_blank=True, required=False, default='')

    def validate(self, data):
        full_name = ' '.join(filter(None, [data['first_name'], data['last_name']]))
        if len(full_name) > 255:
            raise serializers.ValidationError('Your full name must be 255 characters or fewer.')
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    user = AccountSerializer(read_only=True)
    display_name = serializers.CharField(source='Display_name', read_only=True, allow_null=True)
    profile_picture = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = ['user', 'display_name', 'profile_picture', 'created_at', 'updated_at']
        read_only_fields = fields


    def get_profile_picture(self, obj):
        if obj.profile_picture:
            return f'https://res.cloudinary.com/{os.environ.get("CLOUDINARY_CLOUD_NAME")}/{obj.profile_picture}'
        return None
