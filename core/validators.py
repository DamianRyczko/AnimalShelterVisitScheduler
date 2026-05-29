from django.core.exceptions import ValidationError
from django.utils import timezone

#---------------------------- Date ---------------------------
def validate_not_future(value, field_label="Data"):
    """Validates that a given date is not in the future.

    Checks if the provided date value is strictly greater than the current 
    local date. If it is, a Django ValidationError is raised.

    Args:
        value (datetime.date): The date value to be validated.
        field_label (str, optional): The human-readable name of the field 
            used in the error message. Defaults to "Data".

    Raises:
        ValidationError: If the provided date is in the future.
    """
    if value and value > timezone.localdate():
        raise ValidationError(f"{field_label} nie może być w przyszłości.")

def validate_not_past(value, field_label="Data"):
    """Validates that a given date is not in the past.

    Checks if the provided date value is strictly earlier than the current 
    local date. If it is, a Django ValidationError is raised.

    Args:
        value (datetime.date): The date value to be validated.
        field_label (str, optional): The human-readable name of the field 
            used in the error message. Defaults to "Data".

    Raises:
        ValidationError: If the provided date is in the past.
    """
    if value and value < timezone.localdate():
        raise ValidationError(f"{field_label} nie może być w przeszłości")
    
def validate_A_not_after_B(date_A, date_B, label_A = "Data A", label_B = "Data B"):
    """Validates the chronological order of two related dates.

    Checks if `date_A` occurs after `date_B`. If `date_B` is strictly 
    earlier than `date_A` (meaning the end date is before the start date), 
    a Django ValidationError is raised.

    Args:
        date_A (datetime.date): The starting or initial date to compare.
        date_B (datetime.date): The ending or subsequent date to compare.
        label_A (str, optional): The human-readable name for the first date. 
            Defaults to "Data A".
        label_B (str, optional): The human-readable name for the second date. 
            Defaults to "Data B".

    Raises:
        ValidationError: If `date_A` is chronologically after `date_B`.
    """
    if date_A and date_B and date_B < date_A:
        raise ValidationError(f"{label_A} nie może być późniejsza od {label_B}")