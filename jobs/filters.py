import django_filters
from .models import Job, EmploymentType


class JobFilter(django_filters.FilterSet):
    """Filter for jobs list"""

    title = django_filters.CharFilter(lookup_expr='icontains')
    company = django_filters.NumberFilter(field_name='company__id')
    employment_type = django_filters.ChoiceFilter(
        choices=EmploymentType.choices
    )
    location = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    min_salary = django_filters.NumberFilter(
        field_name='salary_min',
        lookup_expr='gte'
    )

    class Meta:
        model = Job
        fields = ['title', 'company', 'employment_type', 'location', 'is_active']