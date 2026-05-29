from django.contrib.auth.models import User
from django.db.models import QuerySet, Model
from django.db import transaction
from django.utils import timezone
from typing import Generic, TypeVar, Type
from .models import Animal, Category, Term, Appointment, Profile
from django.shortcuts import get_object_or_404
T = TypeVar("T", bound=Model)

class BaseRepository(Generic[T]):
    def __init__(self, model: TypeVar[T]):
        self.model: type[T] = model

    def get_all_active(self) -> QuerySet[T]:
        return self.model.objects.filter(is_active=True)
    
    def get_all(self) -> QuerySet[T]:
        return self.model.objects.all()

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
    
class AppointmentRepository(BaseRepository[Appointment]):
    def __init__(self):
        super().__init__(Appointment)

    def category_has_animals(self, category: Category) -> bool:
        return Animal.objects.filter(category=category).exists()

    def category_has_active_animals(self, category: Category) -> bool:
        return Animal.objects.filter(category=category, is_active=True).exists()

class AppointmentRepository(BaseRepository[Appointment]):
    def __init__(self):
        super().__init__(Appointment)

    def get_user_appointments(self, profile_id: int) -> QuerySet[Appointment]:
        return Appointment.objects.filter(user=profile_id).filter(status__in=['P','C','R']).order_by(
            'term__start_date', )

    def get_by_term(self, term: Term) -> Appointment:
        return Appointment.objects.get(term=term)

    def get_user_appointment_history(self, user):
        """
        Retrieves the inactive appointment history for a specific user.
        Filters appointments to include only those that have finalized statuses (completed, cancelled or no-show).

        Args:
            user (Profile): the user profile object to fetch the history for.

        Returns:
            QuerySet[Appointment]: A queryset of finalized user's appointments.
        """
        return Appointment.objects.filter(
            user = user,
            status__in=['D','X','N']
            )

class CategoryRepository(BaseRepository[Category]):
    def __init__(self):
        super().__init__(Category)

class TermRepository(BaseRepository[Term]):
    def __init__(self):
        super().__init__(Term)

    def get_for_update(self, term_id: int) -> Term:
        return Term.objects.select_for_update().get(id=term_id)

    def get_all_active(self) -> QuerySet[Term]:
        Term.objects.filter(is_active=True, start_date__lt=timezone.localdate()).update(is_active=False)
        return super().get_all_active()

    def get_all_for_animal(self, animal_fk: int) -> QuerySet[Term]:
        return Term.objects.filter(animal=animal_fk)
    
    def delete_soft(self, pk: int) -> bool:
        with transaction.atomic():
            success = super().delete_soft(pk)
            if success:
                Appointment.objects.filter(term_id=pk, status='P').update(status='X') # Pending -> Cancelled
            return success

    def animal_has_terms(self, animal: Animal) -> bool:
        return Term.objects.filter(animal=animal).exists()

    def animal_has_active_terms(self, animal: Animal) -> bool:
        return Term.objects.filter(animal=animal, is_active=True).exists()

class ProfileRepository():
    def get_for_update(self, user: User) -> Profile:
        return Profile.objects.select_for_update().get(user=user)

    def get_by_user(self, user: User) -> Profile:
        return get_object_or_404(Profile, user=user)
