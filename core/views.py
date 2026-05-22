from django.shortcuts import render, redirect
from .decorators import allowed_roles
from .services import animal_service, appointment_service, term_service
from .filters import AnimalFilter, AppointmentFilter, TermFilter
from .forms import AnimalForm


#---------------------------- HOME ---------------------------
def home(request):

    animal_queryset = animal_service.get_all()

    animal_filter = AnimalFilter(request.GET, queryset=animal_queryset)

    context = {
        'filter': animal_filter,
        'animals': animal_filter.qs,
    }

    return render(request, 'client/index.html', context)

#---------------------------- CLIENT ---------------------------
@allowed_roles(allowed_groups=['Customers'])
def history(request):
    """
    Renders the user's appointment history view (read-only). Being logged in is required.
    This function retreives user's appointment history and filters it based on the user's choices in the filter form.

    Args:
        request: HTTP request of the user from "Customers" group.

    Returns:
        HttpResponse: Rendered "client/history.html" template containing filter form and list of user's inactive appointments.  
    """
    user = request.user.profile
    base_appointments = appointment_service.get_user_appointment_history(user)
    filtered_appointments = AppointmentFilter(request.GET, queryset=base_appointments)

    context = {
        'filter': filtered_appointments,
        'appointments': filtered_appointments.qs
    }
    return render(request, 'client/history.html', context)

#---------------------------- EMPLOYEE ---------------------------
#@allowed_roles(allowed_groups=['Employees', 'Admins'])
def employee_animals(request):
    animals = animal_service.get_all()
    return render(request, 'employee/employee_animals.html', {'animals': animals})


def animal_detail(request, animal_id):
    animal = animal_service.get_by_id(animal_id)

    term_queryset = term_service.get_all_for_animal(animal)
    term_filter = TermFilter(request.GET, queryset=term_queryset)

    context = {
        'animal': animal,
        'filter': term_filter,
        'terms': term_filter.qs,
    }
    return render(request, 'client/animal_detail.html', context)

#@allowed_roles(allowed_groups=['Employees', 'Admins'])
def manage_animal(request, pk = None):
    animal = animal_service.get_by_id(pk) if pk else None
    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES, instance=animal)
        if form.is_valid():
            animal_obj = form.save(commit=False)
            animal_service.save(animal_obj)
            form.save_m2m()
            return redirect('employee_animals')
    else:
        form = AnimalForm(instance=animal)
    return render(request, 'employee/animals_add.html', {'form': form})

#@allowed_roles(allowed_groups=['Employees', 'Admins'])
def delete_animal(request, pk):
    if request.method == 'POST':
        animal_service.delete(pk)
    return redirect('employee_animals')