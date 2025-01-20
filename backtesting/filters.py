import django_filters
from .models import StockData
from django import forms
from django.db.models import Q

import json
import django_filters
from django import forms
from .models import StockData
#Filter - filtrowanie bazy danych w celu zwrócenie danych spółki giełdowej z konkretnego okresu.

class StockDataFilter(django_filters.FilterSet):
    ticker = django_filters.CharFilter(
        field_name="ticker",
        lookup_expr="iexact",
        label="Ticker",
    )

    start_date = django_filters.DateFilter(
        field_name="timestamp",
        lookup_expr="gte",
        label="Start Date",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    end_date = django_filters.DateFilter(
        field_name="timestamp",
        lookup_expr="lte",
        label="End Date",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = StockData
        fields = ['ticker', 'start_date', 'end_date']
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date must be earlier than end date")
