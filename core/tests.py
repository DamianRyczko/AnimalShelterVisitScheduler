# core/tests.py
from datetime import date

import pytest
from django.contrib.auth.models import User
from django.db import transaction

from core.models import Profile, Category, Animal, Term, Appointment
from core.repositories import (
    AnimalRepository,
    AppointmentRepository,
    CategoryRepository,
    TermRepository,
    ProfileRepository,
    BaseRepository,
)
from core.services import (
    animal_service,
    appointment_service,
    category_service,
    term_service,
    profile_service,
)


def create_profile(username="alice", phone_number="123456789"):
    user = User.objects.create_user(username=username, password="secret")
    return Profile.objects.create(user=user, phone_number=phone_number)


def create_category(title="Dogs", description="Dog category", is_active=True):
    return Category.objects.create(title=title, description=description, is_active=is_active)


def create_animal(category, name="Rex", is_active=True):
    return Animal.objects.create(
        name=name,
        description="A friendly animal",
        admission_date=date(2024, 1, 1),
        category=category,
        is_active=is_active,
    )


def create_term(animal, start_date, end_date, status=True, is_active=True):
    return Term.objects.create(
        start_date=start_date,
        end_date=end_date,
        status=status,
        animal=animal,
        is_active=is_active,
    )


def create_appointment(profile, term, status="P"):
    return Appointment.objects.create(user=profile, term=term, status=status)


@pytest.mark.django_db
def test_base_repository_get_all_and_soft_delete():
    active_category = create_category(title="Dogs")
    inactive_category = create_category(title="Cats", is_active=False)
    repo = BaseRepository(Category)

    assert repo.get_all_active().count() == 1
    assert repo.get_all().count() == 2
    assert repo.delete_soft(active_category.id) is True

    active_category.refresh_from_db()
    assert active_category.is_active is False

    assert repo.delete(inactive_category.id) is True
    assert Category.objects.filter(pk=inactive_category.id).exists() is False


@pytest.mark.django_db
def test_animal_repository_category_has_active_and_any_animals():
    repo = AnimalRepository()
    category = create_category(title="Dogs")
    create_animal(category, is_active=True)

    assert repo.category_has_active_animals(category) is True
    assert repo.category_has_animals(category) is True


@pytest.mark.django_db
def test_appointment_repository_cancel_pending_or_confirmed_for_term():
    user_profile = create_profile("alice")
    category = create_category()
    animal = create_animal(category)
    term = create_term(animal, date(2030, 1, 1), date(2030, 1, 1))
    pending = create_appointment(user_profile, term, status="P")
    confirmed = create_appointment(user_profile, term, status="C")
    rejected = create_appointment(user_profile, term, status="R")

    repo = AppointmentRepository()
    updated_count = repo.cancel_pending_for_term(term)

    assert updated_count == 2
    pending.refresh_from_db()
    confirmed.refresh_from_db()
    rejected.refresh_from_db()
    assert pending.status == "X"
    assert confirmed.status == "X"
    assert rejected.status == "R"


@pytest.mark.django_db
def test_appointment_repository_get_user_appointments_orders_only_active_statuses():
    profile = create_profile("alice")
    category = create_category()
    animal = create_animal(category)
    term_early = create_term(animal, date(2030, 1, 1), date(2030, 1, 1))
    term_late = create_term(animal, date(2030, 2, 1), date(2030, 2, 1))
    create_appointment(profile, term_late, status="C")
    create_appointment(profile, term_early, status="P")
    create_appointment(profile, term_early, status="D")

    repo = AppointmentRepository()
    appointments = list(repo.get_user_appointments(profile.id))

    assert len(appointments) == 2
    assert appointments[0].term_id == term_early.id
    assert appointments[1].term_id == term_late.id


@pytest.mark.django_db
def test_appointment_repository_get_user_appointment_history_returns_finalized():
    profile = create_profile("alice")
    category = create_category()
    animal = create_animal(category)
    term = create_term(animal, date(2030, 1, 1), date(2030, 1, 1))
    create_appointment(profile, term, status="D")
    create_appointment(profile, term, status="X")
    create_appointment(profile, term, status="N")
    create_appointment(profile, term, status="P")

    repo = AppointmentRepository()
    history = list(repo.get_user_appointment_history(profile))

    assert len(history) == 3
    assert {appointment.status for appointment in history} == {"D", "X", "N"}


@pytest.mark.django_db
def test_term_repository_get_all_active_expires_past_terms():
    category = create_category()
    animal = create_animal(category)
    today = date.today()
    past_start = today.replace(year=today.year - 1)
    future_start = today.replace(year=today.year + 1)
    past_term = create_term(animal, past_start, past_start)
    future_term = create_term(animal, future_start, future_start)

    repo = TermRepository()
    active_terms = list(repo.get_all_active())

    assert future_term in active_terms
    assert past_term not in active_terms

    past_term.refresh_from_db()
    assert past_term.is_active is False


@pytest.mark.django_db
def test_profile_repository_get_by_user_and_get_for_update():
    profile = create_profile("alice")
    repo = ProfileRepository()

    assert repo.get_by_user(profile.user) == profile
    with transaction.atomic():
        assert repo.get_for_update(profile.user) == profile


@pytest.mark.django_db
def test_make_appointment_books_available_term():
    user = User.objects.create_user(username="alice", password="secret")
    profile = Profile.objects.create(user=user, phone_number="123456789")
    category = create_category()
    animal = create_animal(category)
    term = create_term(animal, date(2030, 1, 1), date(2030, 1, 1), status=True)

    appointment = appointment_service.make_appointment(user, term.id)

    assert appointment.pk is not None
    assert appointment.user_id == profile.id
    assert appointment.term_id == term.id
    assert appointment.status == "P"

    term.refresh_from_db()
    assert term.status is False


@pytest.mark.django_db
def test_make_appointment_raises_when_term_unavailable():
    profile = create_profile("alice")
    user = profile.user
    category = create_category()
    animal = create_animal(category)
    term = create_term(animal, date(2030, 1, 1), date(2030, 1, 1), status=False)

    with pytest.raises(ValueError):
        appointment_service.make_appointment(user, term.id)


@pytest.mark.django_db
def test_cancel_appointment_releases_term_and_deletes_appointment():
    profile = create_profile("alice")
    category = create_category()
    animal = create_animal(category)
    term = create_term(animal, date(2030, 1, 1), date(2030, 1, 1), status=False)
    appointment = create_appointment(profile, term, status="P")

    result = appointment_service.cancel_appointment(term.id)

    assert result is True
    term.refresh_from_db()
    assert term.status is True
    assert not Appointment.objects.filter(pk=appointment.id).exists()


@pytest.mark.django_db
def test_animal_service_delete_hard_without_linked_terms():
    category = create_category()
    animal = create_animal(category)

    assert animal_service.delete(animal.id) is True
    assert not Animal.objects.filter(pk=animal.id).exists()


@pytest.mark.django_db
def test_animal_service_delete_soft_when_animal_has_only_inactive_terms():
    category = create_category()
    animal = create_animal(category)
    create_term(animal, date(2025, 1, 1), date(2025, 1, 1), status=False, is_active=False)

    assert animal_service.delete(animal.id) is True
    animal.refresh_from_db()
    assert animal.is_active is False


@pytest.mark.django_db
def test_animal_service_delete_raises_when_animal_has_active_term():
    category = create_category()
    animal = create_animal(category)
    create_term(animal, date(2030, 1, 1), date(2030, 1, 1), status=False, is_active=True)

    with pytest.raises(ValueError):
        animal_service.delete(animal.id)


@pytest.mark.django_db
def test_category_service_delete_hard_without_animals():
    category = create_category()

    assert category_service.delete(category.id) is True
    assert not Category.objects.filter(pk=category.id).exists()


@pytest.mark.django_db
def test_category_service_delete_soft_with_inactive_animals():
    category = create_category()
    create_animal(category, is_active=False)

    assert category_service.delete(category.id) is True
    category.refresh_from_db()
    assert category.is_active is False


@pytest.mark.django_db
def test_category_service_delete_raises_when_category_has_active_animals():
    category = create_category()
    create_animal(category, is_active=True)

    with pytest.raises(ValueError):
        category_service.delete(category.id)


@pytest.mark.django_db
def test_term_service_delete_soft_when_term_has_appointment():
    profile = create_profile("alice")
    category = create_category()
    animal = create_animal(category)
    term = create_term(animal, date(2030, 1, 1), date(2030, 1, 1), status=True)
    appointment = create_appointment(profile, term, status="P")

    assert term_service.delete(term.id) is True

    term.refresh_from_db()
    appointment.refresh_from_db()
    assert term.is_active is False
    assert appointment.status == "X"


@pytest.mark.django_db
def test_term_service_delete_hard_when_term_has_no_appointment():
    category = create_category()
    animal = create_animal(category)
    term = create_term(animal, date(2030, 1, 1), date(2030, 1, 1), status=True)

    assert term_service.delete(term.id) is True
    assert not Term.objects.filter(pk=term.id).exists()


@pytest.mark.django_db
def test_term_service_get_all_for_animal_returns_related_terms():
    category = create_category()
    animal = create_animal(category)
    other_animal = create_animal(category, name="Bella")
    term_a = create_term(animal, date(2030, 1, 1), date(2030, 1, 1))
    create_term(other_animal, date(2030, 2, 1), date(2030, 2, 1))

    terms = term_service.get_all_for_animal(animal.id)

    assert list(terms) == [term_a]
