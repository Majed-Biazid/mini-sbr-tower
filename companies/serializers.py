from rest_framework import serializers
from .models import Company
from users.serializers import UserReadSerializer


class CompanyReadSerializer(serializers.ModelSerializer):
    """Serializer for reading company data"""
    user = UserReadSerializer(read_only=True)

    class Meta:
        model = Company
        fields = [
            'id', 'user', 'name', 'logo', 'industry',
            'description', 'website', 'location',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields


class CompanyWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating company"""

    class Meta:
        model = Company
        fields = [
            'name', 'logo', 'industry',
            'description', 'website', 'location'
        ]

    def create(self, validated_data):
        # Automatically link to current user
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data['created_by'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Track who updated
        validated_data['updated_by'] = self.context['request'].user
        return super().update(instance, validated_data)