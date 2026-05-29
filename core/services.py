from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import QuerySet

from .models import Animal, Appointment, Category, Term, Profile
from .repositories import AnimalRepository, AppointmentRepository, CategoryRepository, BaseRepository, TermRepository, ProfileRepository
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseService(Generic[T]):
    """
    A generic base service class that acts as an intermediary layer between 
    views/controllers and data repositories.

    This layer encapsulates business logic and provides a standardized interface 
    for basic CRUD operations, delegating database queries to the underlying repository.
    """
    def __init__(self, repository: BaseRepository[T]) -> None:
        """
        Initializes the base service with a specific repository.

        Args:
            repository (BaseRepository[T]): The repository instance used for 
                data access operations related to the specific model.
        """
        self.repository: BaseRepository[T] = repository

    def get_all(self) -> QuerySet[T]:
        """
        Retrieves all active instances of the model.

        Calls the repository's method to fetch only the records that are 
        currently active (e.g., `is_active=True`).

        Returns:
            QuerySet[T]: A queryset containing active model instances.
        """
        return self.repository.get_all_active()
    
    def get_all_including_inactive(self) -> QuerySet[T]:
        """
        Retrieves all instances of the model, regardless of their active status.

        Returns:
            QuerySet[T]: A complete queryset containing both active and inactive 
                (soft-deleted or past) model instances.
        """
        return self.repository.get_all()

    def get_by_id(self, pk: int) -> T:
        """
        Retrieves a specific model instance by its primary key.

        Args:
            pk (int): The primary key of the instance to retrieve.

        Returns:
            T: The model instance.

        Raises:
            Http404: If the instance with the given primary key does not exist.
        """
        return self.repository.get_by_id(pk)

    def delete(self, pk: int) -> bool:
        """
        Permanently deletes a model instance from the database (Hard Delete).

        Args:
            pk (int): The primary key of the instance to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        return self.repository.delete(pk)
    
    def delete_soft(self, pk: int) -> bool:
        """
        Performs a soft delete on a model instance.

        Usually implemented by toggling a boolean flag (like `is_active=False`) 
        rather than removing the record from the database completely.

        Args:
            pk (int): The primary key of the instance to soft-delete.

        Returns:
            bool: True if the soft deletion was successful, False otherwise.
        """
        return self.repository.delete_soft(pk)

    def save(self, instance: T) -> T:
        """
        Saves or updates a model instance in the database.

        Args:
            instance (T): The model instance to be saved.

        Returns:
            T: The saved model instance.
        """
        return self.repository.save(instance)


class AnimalService(BaseService[Animal]):
    """Service layer handling business logic for the Animal model."""
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
    """Service layer handling business logic for the Appointment model."""
    def __init__(self) -> None:
        super().__init__(AppointmentRepository())

    def get_user_appointments(self, user: User) -> QuerySet[Appointment]:
        profile = profile_service.get_by_user(user)
        return self.repository.get_user_appointments(profile.id)

    def get_user_appointment_history(self, user):
        """
        Retrieves the appointment history for a specific user.

        Args:
            user (Profile): The user profile whose appointment history is requested.

        Returns:
            QuerySet[Appointment]: A queryset of appointments associated with the user.
        """
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
    """Service layer handling business logic for the Category model."""
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
    """Service layer handling business logic for the Term model."""
    def __init__(self) -> None:
        super().__init__(TermRepository())

    def get_for_update(self, term_id: int) -> Term:
        return self.repository.get_for_update(term_id)

    def get_all_for_animal(self, animal_fk: int) -> QuerySet[Term]:
        """
        Retrieves all appointment terms associated with a specific animal.

        Args:
            animal_fk (int): The primary key or ID of the Animal.

        Returns:
            QuerySet[Term]: A queryset containing terms linked to the specified animal.
        """
        return self.repository.get_all_for_animal(animal_fk)

    def is_animal_linked_to_any_term(self, animal: Animal) -> bool:
        return self.repository.animal_has_terms(animal)

    def is_animaly_linked_to_active_term(self, animal: Animal) -> bool:
        return self.repository.animal_has_active_terms(animal)


term_service = TermService()  #module Singleton
