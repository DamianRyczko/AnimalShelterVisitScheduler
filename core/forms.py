from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Animal, Category, GenderChoices, Appointment, AppointmentStatusChoices, Term
from .validators import validate_not_future, validate_A_not_after_B, validate_not_past


class AnimalForm(forms.ModelForm):
    """
    A ModelForm for creating and updating Animal records.

    Handles the input for animal details, including image uploads. It automatically
    limits the category choices to active categories and restricts the UI to 
    prevent selecting future dates for admission and birth.
    """
    class Meta:
        model = Animal
        fields = [
            'name', 'description', 'gender', 'weight',
            'admission_date', 'birth_date', 'category', 'image',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': "Animal's name"}),
            'description': forms.Textarea(attrs={'placeholder': "Animal's description", 'rows': 4}),
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'weight': forms.NumberInput(attrs={'placeholder': "Weight (kg)", 'step': '0.01'}),
            'gender': forms.Select(),
            'category': forms.Select(),
            'image': forms.FileInput(),
        }

    def __init__(self, *args, **kwargs):
        """
        Initializes the form, setting dynamic attributes and querysets.

        Filters the `category` dropdown to show only active categories, sets HTML5 
        'max' attributes on date fields to prevent future date selection in the UI, 
        and appends the 'form-control' CSS class to all widgets.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)

        today_str = timezone.localdate().isoformat()
        self.fields['birth_date'].widget.attrs['max'] = today_str
        self.fields['admission_date'].widget.attrs['max'] = today_str

        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (css + ' form-control').strip()

    def clean(self):
        """
        Validates the cleaned data for the animal form.

        Ensures that neither the birth date nor the admission date is in the future.
        Additionally, it verifies that the birth date logically precedes or equals 
        the admission date.

        Returns:
            dict: The validated and cleaned data dictionary.

        Raises:
            ValidationError: If any date validations fail, errors are attached 
                to the respective fields.
        """
        cleaned_data = super().clean()
        birth_date = cleaned_data.get('birth_date')
        admission_date = cleaned_data.get('admission_date')

        try:
            validate_not_future(birth_date, "Data urodzin")
        except ValidationError as e:
            self.add_error('birth_date', e)

        try:
            validate_not_future(admission_date, "Data przyjęcia")
        except ValidationError as e:
            self.add_error('admission_date', e)

        try:
            validate_A_not_after_B(birth_date, admission_date, "Data urodzin", "daty przyjęcia do schroniska")
        except ValidationError as e:
            self.add_error('admission_date', e)

        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'description']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class TermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ['start_date', 'end_date', 'animal']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'animal': forms.Select()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        today_str = timezone.localdate().isoformat()
        self.fields['start_date'].widget.attrs['min'] = today_str
        self.fields['end_date'].widget.attrs['min'] = today_str
        self.fields['animal'].queryset = Animal.objects.filter(is_active=True)

        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (css + ' form-control').strip()

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        try:
            validate_not_past(start_date, "Początek wizyty")
        except ValidationError as e:
            self.add_error('start_date', e)

        try:
            validate_not_past(end_date, "Koniec wizyty")
        except ValidationError as e:
            self.add_error('end_date', e)

        try:
            validate_A_not_after_B(start_date, end_date, "Data rozpoczęcia wizyty", "daty zakończenia wizyty")
        except ValidationError as e:
            self.add_error('end_date', e)

        return cleaned_data

class AppointmentStateForm(forms.ModelForm):
    """A ModelForm for updating the state of an appointment.

    Only 'status' field of the instance 'Appointment" can be modified. 
    It prevents unauthorized changes to other appointment details (like 
    date, user, or animal) by exposing only the state field.
    """
    class Meta:
        model = Appointment
        fields = ['status']
        
    def clean_status(self):
        """Validates the submitted status value.

        Retrieves the submitted status and checks if it exists within the 
        predefined valid choices (`AppointmentStatusChoices`). This ensures 
        that no invalid state strings can be saved to the database.

        Returns:
            str: The validated and cleaned status code

        Raises:
            ValidationError: If the submitted status is not found in the 
                allowed `AppointmentStatusChoices`.
        """
        status = self.cleaned_data.get('status')
        allowed_states = [choice[0] for choice in AppointmentStatusChoices.choices]
        if status not in allowed_states:
            raise ValidationError("Wybrano niedozwolony status wizyty.")
        return status


class AppointmentStateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status']

    def clean_status(self):
        status = self.cleaned_data.get('status')
        allowed_states = [choice[0] for choice in AppointmentStatusChoices.choices]
        if status not in allowed_states:
            raise ValidationError("Wybrano niedozwolony status wizyty.")
        return status