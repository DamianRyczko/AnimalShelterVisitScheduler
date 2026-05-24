from django.shortcuts import render, redirect
from django.contrib import messages
from .decorators import allowed_roles
from .services import animal_service, term_service, appointment_service
from .filters import AnimalFilter, TermFilter
from .forms import AnimalForm, AppointmentStateForm


#---------------------------- HOME ---------------------------
def home(request):

    animal_queryset = animal_service.get_all()

    animal_filter = AnimalFilter(request.GET, queryset=animal_queryset)

    context = {
        'filter': animal_filter,
        'animals': animal_filter.qs,
    }

    return render(request, 'client/index.html', context)

#---------------------------- EMPLOYEE ---------------------------
#@allowed_roles(allowed_groups=['Employees', 'Admins'])
def employee_animals(request):
    animals = animal_service.get_all()
    return render(request, 'employee/employee_animals.html', {'animals': animals})

@allowed_roles(allowed_groups=['Employees', 'Admins'])
def employee_appointments(request):
    appointments = appointment_service.get_all()

    context = {
        'appointments': appointments
    }
    return render(request, 'employee/employee_appointments.html', context)


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

@allowed_roles(allowed_groups=['Employees', 'Admins'])
def manage_appointment_status(request, pk):
    if request.method == 'POST':
        appointment = appointment_service.get_by_id(pk=pk)
        
        # Przekazujemy request.POST i instancję, by zaktualizować konkretny rekord
        form = AppointmentStateForm(request.POST, instance=appointment)
        
        if form.is_valid():
            form.save()
            messages.success(request, f"Status wizyty #{appointment.id} został zaktualizowany.")
        else:
            messages.error(request, "Wystąpił błąd podczas zmiany statusu.")
            
    return redirect('employee_appointments')

#@allowed_roles(allowed_groups=['Employees', 'Admins'])
def delete_animal(request, pk):
    if request.method == 'POST':
        animal_service.delete(pk)
    return redirect('employee_animals')