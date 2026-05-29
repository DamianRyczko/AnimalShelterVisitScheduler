from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('employee_animals/', views.employee_animals, name='employee_animals'),
    path('animal/add/', views.manage_animal, name='add_animal'),
    path('animal/edit/<int:pk>/', views.manage_animal, name='edit_animal'),
    path('animal/delete/<int:pk>/', views.delete_animal, name='delete_animal'),
    path('animal/<int:animal_id>/', views.animal_detail, name='animal_detail'),
    path('employee_terms/', views.employee_terms, name='employee_terms'),
    path('term/add/', views.manage_term, name='add_term'),
    path('term/edit/<int:pk>/', views.manage_term, name='edit_term'),
    path('term/delete/<int:pk>/', views.delete_term, name='delete_term'),
    path('history/', views.history, name='appointment_history'),
    path('category/add/', views.manage_category, name='add_category'),
    path('category/edit/<int:pk>/', views.manage_category, name='edit_category'),
    path('category/delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('employee_categories/', views.employee_categories, name='employee_categories'),
    path('appointment/', views.appointments, name='appointments'),
    path('cancel_appointment/<int:term_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('make_appointment/<int:term_id>/', views.make_appointment, name='make_appointment'),
]