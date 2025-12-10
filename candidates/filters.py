import django_filters
from .models import Candidate


class CandidateFilter(django_filters.FilterSet):
    """Filter for candidates list"""

    full_name = django_filters.CharFilter(lookup_expr='icontains')
    location = django_filters.CharFilter(lookup_expr='icontains')
    min_experience = django_filters.NumberFilter(
        field_name='experience_years',
        lookup_expr='gte'
    )
    max_experience = django_filters.NumberFilter(
        field_name='experience_years',
        lookup_expr='lte'
    )

    class Meta:
        model = Candidate
        fields = ['full_name', 'location', 'experience_years']
