from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(
        max_length=150,
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        max_length=150,
        write_only=True,
        required=True
    )

    @staticmethod
    def validate_username(value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                {"username": "user with this username already exist"}
            )
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError(
                {"password": "Passwords do not match"}
            )
        return attrs

    def create(self, validated_data: dict) -> User:
        user = User.objects.create_user(
            username=validated_data.get('username'),
            password=validated_data.get('password')
        )
        return user

    def update(self, instance, validated_data: dict) -> None:
        pass
