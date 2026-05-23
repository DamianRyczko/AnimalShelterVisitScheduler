from django.db.models import QuerySet

from .models import Animal, Category, Term
from .repositories import AnimalRepository, CategoryRepository, BaseRepository, TermRepository
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseService(Generic[T]):
    def __init__(self, repository: BaseRepository[T]) -> None:
        self.repository: BaseRepository[T] = repository

    def get_all(self) -> QuerySet[T]:
        return self.repository.get_all_active()

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

animal_service = AnimalService() #module Singleton


class CategoryService(BaseService[Category]):
    def __init__(self) -> None:
        super().__init__(CategoryRepository())

category_service = CategoryService() #module Singleton

class TermService(BaseService[Term]):
    def __init__(self) -> None:
        super().__init__(TermRepository())

    def get_all_for_animal(self, animal_fk: int) -> QuerySet[Term]:
        return self.repository.get_all_for_animal(animal_fk)

term_service = TermService()  #module Singleton
