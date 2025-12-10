from rest_framework import serializers
from .models import User


class UserReadSerializer(serializers.ModelSerializer):
    """Serializer for reading user data (safe to expose)"""

    class Meta:
        model = User
        fields = ['id', 'phone', 'email', 'role', 'first_name', 'last_name',
                  'is_active', 'date_joined']
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        # Phone is required, email is optional
        fields = ['phone', 'email', 'password', 'password_confirm', 'role',
                  'first_name', 'last_name']

    def validate_phone(self, value):
        """Validate phone number format"""
        # Simple validation - you could use phonenumbers library for better validation
        if not value.replace('+', '').isdigit():
            raise serializers.ValidationError('Phone must contain only digits')
        if len(value) < 9:
            raise serializers.ValidationError('Phone number too short')
        return value

    def validate(self, data):
        """Check that passwords match"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Passwords don't match"
            })
        return data

    def create(self, validated_data):
        """Create user with hashed password"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']