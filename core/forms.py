from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Animal, Term, Category, GenderChoices
from .validators import validate_not_future, validate_not_past, validate_A_not_after_B

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
            validate_A_not_after_B(birth_date, admission_date, "Data urodzin", "daty przyjęcia do schroniska")
        except ValidationError as e:
            self.add_error('admission_date', e)

        return cleaned_data
    
class TermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ['start_date', 'end_date', 'animal']
        widgets = {
            'start_date': forms.DateInput(attrs={'type':'date'}),
            'end_date': forms.DateInput(attrs={'type':'date'}),
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