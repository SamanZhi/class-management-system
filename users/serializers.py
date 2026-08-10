from django.core import serializers

from users.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'role',
            'first_name',
            'last_name',
            'phone_number',
            'emergency_number'
        ]

        read_only_fields = ['id', 'username', 'role']