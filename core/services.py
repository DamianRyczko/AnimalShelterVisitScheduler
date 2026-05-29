from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import QuerySet

from .models import Animal, Appointment, Category, Term, Profile
from .repositories import AnimalRepository, AppointmentRepository, CategoryRepository, BaseRepository, TermRepository, ProfileRepository
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseService(Generic[T]):
    def __init__(self, repository: BaseRepository[T]) -> None:
        self.repository: BaseRepository[T] = repository

    def get_all(self) -> QuerySet[T]:
        return self.repository.get_all_active()
    
    def get_all_including_inactive(self) -> QuerySet[T]:
        return self.repository.get_all()

    def get_by_id(self, pk: int) -> T:
        return self.repository.get_by_id(pk)

    def delete(self, pk: int) -> bool:
        return self.repository.delete(pk)
    
    def delete_soft(self, pk: int) -> bool:
        return self.repository.delete_soft(pk)

    def save(self, instance: T) -> T:
        return self.repository.save(instance)


class AnimalService(BaseService[Animal]):
    def __init__(self) -> None:
        super().__init__(AnimalRepository())

    def is_category_linked_to_any_animal(self, category: Category) -> bool:
        return self.repository.category_has_animals(category)

    def is_category_linked_to_active_animal(self, category: Category) -> bool:
        return self.repository.category_has_active_animals(category)

    def delete(self, pk: int) -> bool:
        with transaction.atomic():
            animal = self.get_by_id(pk)
            if term_service.is_animaly_linked_to_active_term(animal):
                raise ValueError(
                    "Cannot delete animal: animal has active terms, please delete terms first.")
            if term_service.is_animal_linked_to_any_term(animal):
                return self.delete_soft(pk)
            return self.repository.delete(pk)

animal_service = AnimalService() #module Singleton

class ProfileService():
    def __init__(self) -> None:
        self.repository: ProfileRepository = ProfileRepository()

    def get_for_update(self, user: User) -> Profile:
        return self.repository.get_for_update(user)

    def get_by_user(self, user: User) -> Profile:
        return self.repository.get_by_user(user)

profile_service = ProfileService()

class AppointmentService(BaseService[Appointment]):
    def __init__(self) -> None:
        super().__init__(AppointmentRepository())

    def get_user_appointments(self, user: User) -> QuerySet[Appointment]:
        profile = profile_service.get_by_user(user)
        return self.repository.get_user_appointments(profile.id)

    def get_user_appointment_history(self, user):
        return self.repository.get_user_appointment_history(user)

    def get_by_term(self, term: Term) -> Appointment:
        return self.repository.get_by_term(term)

    @transaction.atomic
    def make_appointment(self, user: User, term_id: int) -> Appointment:
        profile = profile_service.get_for_update(user)
        term = term_service.get_for_update(term_id)

        if not term.status:
            raise ValueError("This term is already booked.")

        appointment = Appointment(user_id=profile.id, term_id=term_id)
        appointment = self.repository.save(appointment)

        term.status = False  # mark the term as taken
        term.save(update_fields=["status"])
        return appointment

    @transaction.atomic
    def cancel_appointment(self, term_id: int) -> bool:
        term = term_service.get_for_update(term_id)
        appointment = self.repository.get_by_term(term)

        term.status = True
        term.save(update_fields=["status"])

        return self.repository.delete(appointment.id)

    
appointment_service = AppointmentService() #module Singleton

class CategoryService(BaseService[Category]):
    def __init__(self) -> None:
        super().__init__(CategoryRepository())

    def delete(self, pk: int) -> bool:
        with transaction.atomic():
            category = self.get_by_id(pk)
            if animal_service.is_category_linked_to_active_animal(category):
                raise ValueError(
                    "Cannot delete category: It contains active animals. Please deactivate animals first.")
            if animal_service.is_category_linked_to_any_animal(category):
                return self.delete_soft(pk)
            return self.repository.delete(pk)

category_service = CategoryService() #module Singleton

class TermService(BaseService[Term]):
    def __init__(self) -> None:
        super().__init__(TermRepository())

    def get_for_update(self, term_id: int) -> Term:
        return self.repository.get_for_update(term_id)

    def get_all_for_animal(self, animal_fk: int) -> QuerySet[Term]:
        return self.repository.get_all_for_animal(animal_fk)

    def is_animal_linked_to_any_term(self, animal: Animal) -> bool:
        return self.repository.animal_has_terms(animal)

    def is_animaly_linked_to_active_term(self, animal: Animal) -> bool:
        return self.repository.animal_has_active_terms(animal)


term_service = TermService()  #module Singleton
