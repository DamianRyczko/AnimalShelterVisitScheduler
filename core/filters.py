import django_filters
from django import forms
from .models import Animal, Term
from .services import animal_service
class AnimalFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains', label='Szukaj zwierzaka')

    ordering = django_filters.OrderingFilter(
        fields=(('weight', 'weight'),('birth_date', 'date')),
        field_labels = {
            'weight': 'Waga',
            'birth_date': 'Data urodzenia',
        },
        label = 'Sortuj według')

    class Meta:
        model = Animal
        fields = ['category', 'gender']

class TermFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='gte',
        label='Szukaj daty startu',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'date-input'})
    )
    end_date = django_filters.DateFilter(
        field_name='end_date',
        lookup_expr='lte',
        label='Szukaj daty konca',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'date-input'})
    )

    class Meta:
        model = Term
        fields = ['start_date', 'end_date']

class TermFilterEmployee(TermFilter):
    animal = django_filters.ModelChoiceFilter(
        queryset=animal_service.get_all_including_inactive(),
        empty_label='Wszystkie zwierzęta',
        label='Wybierz zwierzaka',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_active = django_filters.BooleanFilter(
        widget = forms.CheckboxInput(),
        label='Ukryj nieaktywne',
        method='filter_active'
    )

    def filter_active(self, queryset, name, value):
        if value is True:
            return queryset.filter(is_active=True)
        return queryset
    
    class Meta:
        fields = TermFilter.Meta.fields + ['animal', 'is_active']