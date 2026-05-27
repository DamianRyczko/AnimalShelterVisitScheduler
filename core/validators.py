from django.core.exceptions import ValidationError
from django.utils import timezone

#---------------------------- Date ---------------------------
def validate_not_future(value, field_label="Data"):
    if value and value > timezone.localdate():
        raise ValidationError(f"{field_label} nie może być w przyszłości.")

def validate_not_past(value, field_label="Data"):
    if value and value < timezone.localdate():
        raise ValidationError(f"{field_label} nie może być w przeszłości")
    
def validate_A_not_after_B(date_A, date_B, label_A = "Data A", label_B = "Data B"):
    if date_A and date_B and date_B < date_A:
        raise ValidationError(f"{label_A} nie może być późniejsza od {label_B}")