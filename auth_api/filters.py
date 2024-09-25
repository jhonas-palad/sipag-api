from django_filters import rest_framework as filters

from .models import User


class ProductFilter(filters.FilterSet):
    name = filters.BooleanFilter(lookup_expr="iexact")

    class Meta:
        model = User
        fields = ["price", "release_date"]
