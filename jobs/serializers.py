from rest_framework import serializers
from .models import Job
from companies.serializers import CompanyReadSerializer


class JobReadSerializer(serializers.ModelSerializer):
    """Serializer for reading job data"""
    company = CompanyReadSerializer(read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'company', 'title', 'description',
            'requirements', 'required_skills', 'employment_type',
            'location', 'salary_min', 'salary_max', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields


class JobListSerializer(serializers.ModelSerializer):
    """Lighter serializer for job list"""
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'company_name', 'title', 'employment_type',
            'location', 'salary_min', 'salary_max', 'is_active',
            'created_at'
        ]


class JobWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating jobs"""

    class Meta:
        model = Job
        fields = [
            'title', 'description', 'requirements',
            'required_skills', 'employment_type', 'location',
            'salary_min', 'salary_max', 'is_active'
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        # Get the user's company
        validated_data['company'] = user.company
        validated_data['created_by'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super().update(instance, validated_data)