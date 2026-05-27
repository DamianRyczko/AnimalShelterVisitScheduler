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
    """Renders the appointment management page for employees.

    Fetches all customer appointments using the appointment service and checks 
    the URL for an 'edit' query parameter. If a valid numeric ID is provided, 
    it is passed to the context to enable inline editing mode for that specific 
    appointment in the template.

    Args:
        request (HttpRequest): The incoming HTTP request object containing 
            potential GET parameters.

    Returns:
        HttpResponse: The rendered 'employee/employee_appointments.html' 
            template populated with the appointments list and the active edit ID.
    """
    appointments = appointment_service.get_all()
    
    edit_id = request.GET.get('edit')
    if edit_id and edit_id.isdigit():
        edit_id = int(edit_id)
    else:
        edit_id = None
    
    context = {
        'appointments': appointments,
        'edit_id': edit_id 
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
    """Handles the status update for a specific customer appointment.

    Processes POST requests to modify the state of an existing appointment 
    using the `AppointmentStateForm`. It fetches the appointment by its 
    primary key, validates the new status, updates the database, and adds 
    an appropriate success or error flash message. Non-POST requests are 
    ignored, and the view always redirects back to the appointments list.

    Args:
        request (HttpRequest): The incoming HTTP request object.
        pk (int): The primary key (ID) of the appointment to be updated.

    Returns:
        HttpResponseRedirect: A redirection to the 'employee_appointments' 
            view, regardless of the request method or validation outcome.
    """
    if request.method == 'POST':
        appointment = appointment_service.get_by_id(pk=pk)
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