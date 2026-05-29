from django.shortcuts import render, redirect
from django.contrib import messages
from .decorators import allowed_roles
from .services import animal_service, appointment_service, term_service, category_service
from .filters import AnimalFilter, AppointmentFilter, TermFilter, TermFilterEmployee, ActiveAppointmentFilter
from .forms import AnimalForm, TermForm, CategoryForm, AppointmentStateForm


#---------------------------- HOME ---------------------------
def home(request):
    """
    Renders the home/index page for clients.

    Fetches all active animals using the animal service and applies the 
    AnimalFilter based on the user's GET request parameters.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        HttpResponse: Rendered 'client/index.html' template containing the 
            filter form and the filtered list of animals.
    """
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

def animal_detail(request, animal_id):
    animal = animal_service.get_by_id(animal_id)

    term_queryset = term_service.get_all_for_animal(animal)
    term_filter = TermFilter(request.GET, queryset=term_queryset)
    user_appointments = appointment_service.get_user_appointments(request.user)
    reserved_terms = [appointment.term for appointment in user_appointments]

    context = {
        'animal': animal,
        'filter': term_filter,
        'terms': term_filter.qs,
        'user_reserved_terms': reserved_terms,
    }
    return render(request, 'client/animal_detail.html', context)

def appointments(request):
    appointments_queryset = appointment_service.get_user_appointments(request.user)
    appointments_filter = ActiveAppointmentFilter(request.GET, queryset=appointments_queryset)
    context = {
        'filter': appointments_filter,
        'appointments': appointments_filter.qs
    }
    return render(request, 'client/apointments.html', context)

def make_appointment(request, term_id):
    if request.method == 'POST':
        appointment_service.make_appointment(request.user, term_id)
    return redirect(request.POST.get('next') or 'appointments')


def cancel_appointment(request, term_id):
    if request.method == 'POST':
        appointment_service.cancel_appointment(term_id)

    return redirect(request.POST.get('next') or 'appointments')

#---------------------------- EMPLOYEE ---------------------------
@allowed_roles(allowed_groups=['Employees', 'Admins'])
def employee_animals(request):
    """
    Renders the employee's view for managing animals.

    Retrieves a list of all active animals from the database to display 
    on the employee management panel.

    Args:
        request (HttpRequest): HTTP request of the user from "Employees" or "Admins" group.

    Returns:
        HttpResponse: Rendered 'employee/employee_animals.html' template containing 
            the list of animals.
    """
    animals = animal_service.get_all()
    return render(request, 'employee/employee_animals.html', {'animals': animals})

@allowed_roles(allowed_groups=['Employees', 'Admins'])
def employee_terms(request):
    """
    Renders the employee's view for managing terms. Past terms are read-only.
    User may filter the terms list based on start/end date, animal it's connected to or is_active status.

    Args:
        request: HTTP request of the user from "Employees" or "Admins" group.

    Returns:
        HttpResponse: Rendered "employee/employee_terms.html" template containing filter form and list of all terms in database. 
    """
    terms = term_service.get_all_including_inactive()  
    term_filter = TermFilterEmployee(request.GET, queryset=terms)
    
    context = {
        'filter': term_filter,
        'terms': term_filter.qs
        }
    
    return render(request, 'employee/employee_terms.html', context)


def animal_detail(request, animal_id):
    """
    Displays the detailed view of a specific animal and its available terms.

    Fetches the animal object by its ID and retrieves all terms associated 
    with it. Allows the user to filter the animal's terms using the TermFilter.

    Args:
        request (HttpRequest): The incoming HTTP request.
        animal_id (int): The unique identifier of the animal.

    Returns:
        HttpResponse: Rendered 'client/animal_detail.html' template containing 
            animal details, term filter form, and the filtered list of terms.
    """
    animal = animal_service.get_by_id(animal_id)


@allowed_roles(allowed_groups=['Employees', 'Admins'])
def manage_animal(request, pk = None):
    """
    Handles the creation of a new animal or the modification of an existing one.

    Processes both GET (displaying the form) and POST (saving data) requests. 
    It supports file uploads through request.FILES and handles many-to-many 
    relationships if necessary.

    Args:
        request (HttpRequest): HTTP request of the user from "Employees" or "Admins" group.
        pk (int, optional): Primary key of the animal to edit. Defaults to None for creating a new animal.

    Returns:
        HttpResponseRedirect: Redirects to the 'employee_animals' view upon successful save.
        HttpResponse: Rendered 'employee/animals_add.html' template with the form otherwise.
    """
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
def manage_term(request, pk=None):
    """
    Allows to add a new term or edit the exited one. You can only add or edit future term.

    Args:
        request: HTTP request of the user from "Employees" or "Admins" group.
        pk: primary key of the term to edit (optional)
    
    Returns:
        HttpResponseRedirect: Redirects to the "employee/employee_terms.html" template containing filter form and list of all terms in database. 
    """
    term = term_service.get_by_id(pk) if pk else None

    if term and term.is_past():
        messages.error(request, "Nie możesz edytować terminu z przeszłości.")
        return redirect('employee_terms')
    
    if request.method == 'POST':
        form = TermForm(request.POST, instance=term)
        if form.is_valid():
            term_obj = form.save(commit=False)
            term_service.save(term_obj)
            form.save_m2m()

            if pk:
                messages.success(request, 'Termin został pomyślnie zaktualizowany.')
            else:
                messages.success(request, 'Nowy termin został pomyślnie dodany.')

            return redirect('employee_terms')
    else:
        form = TermForm(instance=term)
    return render(request, 'employee/term_add.html', {'form': form})

@allowed_roles(allowed_groups=['Employees', 'Admins'])
def delete_animal(request, pk):
    """
    Performs a SOFT delete operation on a specific animal.

    Processes POST requests to safely remove an animal from public/employee 
    listings by changing its is_active status rather than permanently deleting 
    it from the database.

    Args:
        request (HttpRequest): HTTP request of the user from "Employees" or "Admins" group.
        pk (int): Primary key of the animal to be soft-deleted.

    Returns:
        HttpResponseRedirect: Redirects to the 'employee_animals' view after deletion.
    """
    if request.method == 'POST':
        try:
            animal_service.delete(pk)
            messages.success(request, 'Animal deleted')
        except ValueError as e:
            messages.error(request, str(e))
    return redirect('employee_animals')

@allowed_roles(allowed_groups=['Employees', 'Admins'])
def delete_term(request, pk):
    """
    Deletes the term from database via soft delete operation. Deleted term mustn't be from the past.

    Args:
        request: HTTP request of the user from "Employees" or "Admins" group.
        pk: primary key of the term to delete
    
    Returns:
        HttpResponseRedirect: Redirects to the "employee/employee_terms.html" template containing filter form and list of all terms in database. 
    """
    if request.method == 'POST':
        term = term_service.get_by_id(pk)
        if term.is_past():
            messages.error(request, "Nie możesz usunąć terminu z przeszłości.")
        else:
            term_service.delete_soft(pk)
            messages.success(request, "Termin usunięty pomyślnie.")
    return redirect('employee_terms')


@allowed_roles(allowed_groups=['Employees', 'Admins'])
def employee_categories(request):
    categories = category_service.get_all()
    return render(request, 'employee/employee_categories.html', {'categories': categories})
@allowed_roles(allowed_groups=['Employees', 'Admins'])
def manage_category(request, pk=None):
    category = category_service.get_by_id(pk) if pk else None

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_obj = form.save(commit=False)
            category_service.save(category_obj)
            form.save_m2m()

            return redirect('employee_categories')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'employee/category_add.html', {'form': form})
@allowed_roles(allowed_groups=['Employees', 'Admins'])
def delete_category(request, pk):
    if request.method == 'POST':
        try:
            category_service.delete(pk)
            messages.success(request, 'Category deleted')
        except ValueError as e:
            messages.error(request, str(e))
    return redirect('employee_categories')

@allowed_roles(allowed_groups=['Employees', 'Admins'])
def employee_appointments(request):
    appointments = appointment_service.get_all()

    context = {
        'appointments': appointments
    }
    return render(request, 'employee/employee_appointments.html', context)


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