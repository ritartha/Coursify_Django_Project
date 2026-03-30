import django_filters
from .models import Course


class CourseFilter(django_filters.FilterSet):
    """Filter courses by various criteria."""
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    instructor = django_filters.NumberFilter(field_name='instructor__id')
    category = django_filters.CharFilter(field_name='category')
    is_free = django_filters.BooleanFilter(method='filter_is_free')

    class Meta:
        model = Course
        fields = ['category', 'instructor', 'is_published']

    def filter_is_free(self, queryset, name, value):
        if value:
            return queryset.filter(price=0)
        return queryset.filter(price__gt=0)
