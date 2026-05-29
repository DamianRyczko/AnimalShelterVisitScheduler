from django.db import models
from django.conf import settings
from django.utils import timezone

class Profile(models.Model):
    # Link to the built-in Django User
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    class Meta:
        ordering = ['user__last_name', 'user__first_name']

class Category(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Categories"  # Fixes "Categorys" in Admin

class GenderChoices(models.TextChoices):
    FEMALE = 'F', 'Female'
    MALE = 'M', 'Male'
    OTHER = 'O', 'Other'

class Animal(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    gender = models.CharField( max_length=1, choices=GenderChoices.choices, default=GenderChoices.OTHER)
    admission_date = models.DateField()
    birth_date = models.DateField(null=True, blank=True)
    weight = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='media/animals/images')
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name


class Term(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.BooleanField(default=True) #free = 1 / taken = 0
    animal = models.ForeignKey(Animal, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)

    def is_past(self):
        return self.start_date < timezone.now().date()

    #Prevent start_date after end_date
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='term_end_after_start',
            ),
        ]

class AppointmentStatusChoices(models.TextChoices):
    PENDING = 'P', 'Pending'
    CONFIRMED = 'C', 'Confirmed'
    REJECTED = 'R', 'Rejected'
    
    COMPLETED = 'D', 'Completed'
    CANCELLED = 'X', 'Cancelled'
    NO_SHOW = 'N', 'No Show'

class Appointment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=1, choices=AppointmentStatusChoices.choices, default=AppointmentStatusChoices.PENDING)
    user = models.ForeignKey(Profile, on_delete=models.PROTECT)
    term = models.ForeignKey(Term, on_delete=models.PROTECT)
    is_active= models.BooleanField(default=True)

