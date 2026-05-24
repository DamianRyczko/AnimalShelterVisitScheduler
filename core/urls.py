from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('employee_animals/', views.employee_animals, name='employee_animals'),
    path('animal/add/', views.manage_animal, name='add_animal'),
    path('animal/edit/<int:pk>/', views.manage_animal, name='edit_animal'),
    path('animal/delete/<int:pk>/', views.delete_animal, name='delete_animal'),
    path('animal/<int:animal_id>/', views.animal_detail, name='animal_detail'),
    path('employee/appointments/', views.employee_appointments, name='employee_appointments'),
    path('employee/appointments/<int:pk>/update-status/', views.manage_appointment_status, name='update_appointment_status'),

]