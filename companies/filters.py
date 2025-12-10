import django_filters
from .models import Company, Industry


class CompanyFilter(django_filters.FilterSet):
    """Filter for companies list"""

    name = django_filters.CharFilter(lookup_expr='icontains')
    industry = django_filters.ChoiceFilter(choices=Industry.choices)
    location = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Company
        fields = ['name', 'industry', 'location']