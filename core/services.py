from django.db.models import QuerySet

from .models import Animal, Appointment, Category, Term
from .repositories import AnimalRepository, AppointmentRepository, CategoryRepository, BaseRepository, TermRepository
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

animal_service = AnimalService() #module Singleton

class AppointmentService(BaseService[Appointment]):
    """Service layer handling business logic for the Appointment model."""
    def __init__(self) -> None:
        super().__init__(AppointmentRepository())

    def get_user_appointment_history(self, user):
        """
        Retrieves the appointment history for a specific user.

        Args:
            user (Profile): The user profile whose appointment history is requested.

        Returns:
            QuerySet[Appointment]: A queryset of appointments associated with the user.
        """
        return self.repository.get_user_appointment_history(user)
    
appointment_service = AppointmentService() #module Singleton

class CategoryService(BaseService[Category]):
    """Service layer handling business logic for the Category model."""
    def __init__(self) -> None:
        super().__init__(CategoryRepository())

category_service = CategoryService() #module Singleton

class TermService(BaseService[Term]):
    """Service layer handling business logic for the Term model."""
    def __init__(self) -> None:
        super().__init__(TermRepository())

    def get_all_for_animal(self, animal_fk: int) -> QuerySet[Term]:
        """
        Retrieves all appointment terms associated with a specific animal.

        Args:
            animal_fk (int): The primary key or ID of the Animal.

        Returns:
            QuerySet[Term]: A queryset containing terms linked to the specified animal.
        """
        return self.repository.get_all_for_animal(animal_fk)

term_service = TermService()  #module Singleton
