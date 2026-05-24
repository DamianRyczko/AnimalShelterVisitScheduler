from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Animal, Category,GenderChoices, Appointment, AppointmentStatusChoices
from .validators import validate_admission_after_birth, validate_not_future

class AnimalForm(forms.ModelForm):
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
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)

        today_str = timezone.localdate().isoformat()
        self.fields['birth_date'].widget.attrs['max'] = today_str
        self.fields['admission_date'].widget.attrs['max'] = today_str

        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (css + ' form-control').strip()

    def clean(self):
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
            validate_admission_after_birth(birth_date, admission_date)
        except ValidationError as e:
            self.add_error('admission_date', e)

        return cleaned_data
    
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