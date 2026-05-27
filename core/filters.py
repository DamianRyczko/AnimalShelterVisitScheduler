import django_filters
from django import forms
from .models import Animal, AppointmentStatusChoices, Term, Appointment
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

class AppointmentFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(
        choices=[
            (AppointmentStatusChoices.COMPLETED, 'Completed'),
            (AppointmentStatusChoices.CANCELLED, 'Cancelled'),
            (AppointmentStatusChoices.NO_SHOW, 'No Show'),
        ],
        label='Status wizyty',
        widget=forms.Select(attrs={'class': 'select-input'})
    )

    start_date = django_filters.DateFilter(
        field_name='term__start_date',
        lookup_expr='gte',
        label='Data od',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'date-input'})
    )
    
    end_date = django_filters.DateFilter(
        field_name='term__end_date',
        lookup_expr='lte',
        label='Data do',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'date-input'})
    )   

    animal = django_filters.ModelChoiceFilter(
        field_name='term__animal',
        queryset=Animal.objects.filter(is_active=True),
        label='Zwierzę',
        widget=forms.Select(attrs={'class': 'select-input'})
    )

    class Meta:
        model = Appointment
        fields = ['status', 'start_date', 'end_date', 'animal']