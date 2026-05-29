import django_filters
from django import forms
from .models import Animal, AppointmentStatusChoices, Term, Appointment
from .services import animal_service
class AnimalFilter(django_filters.FilterSet):
    """
    A filter set for the Animal model.

    Allows users to search for animals by title (partial match), filter by 
    category and gender, and order the results by weight or birth date.
    """
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
    """
    A base filter set for the Term model.

    Provides basic filtering capabilities to find appointment terms that 
    start on or after a specific date, and end on or before a specific date.
    """
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
    """
    An extended Term filter set for employee management.

    Inherits from `TermFilter` and adds the ability to filter terms by a 
    specific animal and to hide inactive (soft-deleted or past) terms.
    """
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
        """Filters the queryset to include only active terms.

        Args:
            queryset (QuerySet): The initial queryset of terms.
            name (str): The name of the field being filtered.
            value (bool): The boolean value from the checkbox.

        Returns:
            QuerySet: A filtered queryset containing only active terms if 
                `value` is True, otherwise returns the original queryset.
        """
        if value is True:
            return queryset.filter(is_active=True)
        return queryset
    
    class Meta:
        fields = TermFilter.Meta.fields + ['animal', 'is_active']
class AppointmentFilter(django_filters.FilterSet):
    """
    A filter set for the Appointment model.

    Allows users to filter their appointment history by status, a specific 
    date range (based on the associated term's start and end dates), and 
    the specific animal involved.
    """
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


class ActiveAppointmentFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(
        choices=[
            (AppointmentStatusChoices.PENDING, 'Pending'),
            (AppointmentStatusChoices.CONFIRMED, 'Confirmed'),
            (AppointmentStatusChoices.REJECTED, 'Rejected'),
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
