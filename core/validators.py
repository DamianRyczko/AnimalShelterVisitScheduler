from django.core.exceptions import ValidationError
from django.utils import timezone

#---------------------------- Date ---------------------------
def validate_not_future(value, field_label="Data"):
    if value and value > timezone.localdate().isoformat():
        raise ValidationError(f"{field_label} nie może być w przyszłości.")

def validate_admission_after_birth(birth_date, admission_date):
    if birth_date and admission_date and admission_date < birth_date:
        raise ValidationError("Data przyjęcia do schroniska nie może być wcześniejsza niż data urodzin.")