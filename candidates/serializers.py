from rest_framework import serializers
from .models import Candidate
from users.serializers import UserReadSerializer


class CandidateReadSerializer(serializers.ModelSerializer):
    """Serializer for reading candidate data"""
    user = UserReadSerializer(read_only=True)

    class Meta:
        model = Candidate
        fields = [
            'id', 'user', 'full_name', 'phone', 'cv_file',
            'skills', 'experience_years', 'location', 'bio',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields


class CandidateWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating candidate"""

    class Meta:
        model = Candidate
        fields = [
            'full_name', 'phone', 'cv_file',
            'skills', 'experience_years', 'location', 'bio'
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data['created_by'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super().update(instance, validated_data)