from django.shortcuts import render, redirect
from django.contrib import messages
from .decorators import allowed_roles
from .services import animal_service, term_service
from .filters import AnimalFilter, TermFilter, TermFilterEmployee
from .forms import AnimalForm, TermForm


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
def employee_terms(request):
    terms = term_service.get_all_including_inactive()  
    term_filter = TermFilterEmployee(request.GET, queryset=terms)
    
    context = {
        'filter': term_filter,
        'terms': term_filter.qs
        }
    
    return render(request, 'employee/employee_terms.html', context)


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
def manage_term(request, pk=None):
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

#@allowed_roles(allowed_groups=['Employees', 'Admins'])
def delete_animal(request, pk):
    if request.method == 'POST':
        animal_service.delete_soft(pk)
    return redirect('employee_animals')

@allowed_roles(allowed_groups=['Employees', 'Admins'])
def delete_term(request, pk):
    if request.method == 'POST':
        term = term_service.get_by_id(pk)
        if term.is_past():
            messages.error(request, "Nie możesz usunąć terminu z przeszłości.")
        else:
            term_service.delete_soft(pk)
            messages.success(request, "Termin usunięty pomyślnie.")
    return redirect('employee_terms')
