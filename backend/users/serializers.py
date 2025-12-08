from rest_framework import serializers
from .models import User, Client


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_client', 'is_admin_user']

    def create(self, validated_data):
        # Перевизначаємо створення, щоб хешувати пароль
        user = User.objects.create_user(**validated_data)
        return user


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
