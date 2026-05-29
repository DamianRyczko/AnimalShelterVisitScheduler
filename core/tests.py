# core/tests.py
from datetime import date

import pytest
from django.contrib.auth.models import User

from core.models import Profile, Category, Animal, Term, Appointment
from core.repositories import AnimalRepository
from core.services import appointment_service


# ---------- repository test ----------

@pytest.mark.django_db
def test_animal_repository_category_has_active_animals():
    repo = AnimalRepository()
    category = Category.objects.create(title="Dogs", description="Dog category")
    Animal.objects.create(
        name="Rex",
        description="A friendly dog",
        admission_date=date(2024, 1, 1),
        category=category,
        is_active=True,
    )

    assert repo.category_has_active_animals(category) is True
    assert repo.category_has_animals(category) is True


# ---------- service test ----------

@pytest.mark.django_db
def test_make_appointment_books_available_term():
    user = User.objects.create_user(username="alice", password="secret")
    profile = Profile.objects.create(user=user, phone_number="123456789")
    category = Category.objects.create(title="Dogs", description="Dog category")
    animal = Animal.objects.create(
        name="Rex",
        description="A friendly dog",
        admission_date=date(2024, 1, 1),
        category=category,
    )
    term = Term.objects.create(
        start_date=date(2030, 1, 1),
        end_date=date(2030, 1, 1),   # >= start_date, satisfies the CheckConstraint
        status=True,                 # available
        animal=animal,
    )

    appointment = appointment_service.make_appointment(user, term.id)

    assert appointment.pk is not None
    assert appointment.user_id == profile.id   # Appointment.user FK points at Profile
    assert appointment.term_id == term.id
    assert appointment.status == "P"           # default Pending

    term.refresh_from_db()
    assert term.status is False                # term flipped to taken