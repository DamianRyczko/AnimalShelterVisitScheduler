from django.contrib import admin
from .models import Appointment, Animal, Term, Category

admin.site.register(Appointment)
admin.site.register(Animal)
admin.site.register(Term)
admin.site.register(Category)