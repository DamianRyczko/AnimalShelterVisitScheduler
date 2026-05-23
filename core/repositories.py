from django.db.models import QuerySet, Model
from typing import Generic, TypeVar, Type
from core.models import Animal
from .models import Animal, Category, Term, Appointment
from django.shortcuts import get_object_or_404
T = TypeVar("T", bound=Model)

class BaseRepository(Generic[T]):
    def __init__(self, model: TypeVar[T]):
        self.model: type[T] = model

    def get_all_active(self) -> QuerySet[T]:
        return self.model.objects.filter(is_active=True)

    def get_by_id(self, pk: int) -> T:
        return get_object_or_404(self.model, pk=pk)


    def delete(self, pk: int) -> bool:
        deleted_count, _ = self.model.objects.filter(pk=pk).delete()
        return deleted_count > 0

    def delete_soft(self, pk:int) -> bool:
        updated_count = self.model.objects.filter(pk=pk, is_active=True).update(is_active=False)
        return updated_count > 0

    def save(self, instance: T) -> T:
        instance.save()
        return instance

class AnimalRepository(BaseRepository[Animal]):
    def __init__(self):
        super().__init__(Animal)

class CategoryRepository(BaseRepository[Category]):
    def __init__(self):
        super().__init__(Category)

class TermRepository(BaseRepository[Term]):
    def __init__(self):
        super().__init__(Term)

    def get_all_for_animal(self, animal_fk: int) -> QuerySet[Term]:
        return Term.objects.filter(animal=animal_fk)