from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_client', 'is_admin_user', 'is_superuser', 'is_staff']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
