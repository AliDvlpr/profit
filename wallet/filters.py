from django_filters.rest_framework import FilterSet
from rest_framework.filters import BaseFilterBackend
from .models import *

class TransactionFilter(FilterSet):
    class Meta:
        model = Transaction
        fields = {
            'action': ['exact'],
            'status': ['exact']
        }