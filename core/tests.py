from datetime import date

import pytest

from core.models import Chore, ChoreRotationSlot, Completion, Member


@pytest.mark.django_db
def test_django_settings_are_loaded():
    from django.conf import settings

    assert "core" in settings.INSTALLED_APPS


@pytest.mark.django_db
def test_member_str_is_its_name():
    member = Member.objects.create(name="Alex")
    assert str(member) == "Alex"


@pytest.mark.django_db
def test_fixed_chore_keeps_its_assignee():
    alex = Member.objects.create(name="Alex")
    chore = Chore.objects.create(
        name="Take out trash",
        assignment_type=Chore.AssignmentType.FIXED,
        recurrence_interval_days=7,
        fixed_assignee=alex,
    )
    assert chore.fixed_assignee == alex
    assert chore.assignment_type == Chore.AssignmentType.FIXED


@pytest.mark.django_db
def test_rotating_chore_has_an_ordered_member_cycle():
    alex = Member.objects.create(name="Alex")
    sam = Member.objects.create(name="Sam")
    chore = Chore.objects.create(
        name="Wash dishes",
        assignment_type=Chore.AssignmentType.ROTATING,
        recurrence_interval_days=1,
        rotation_current=alex,
    )
    ChoreRotationSlot.objects.create(chore=chore, member=alex, order=0)
    ChoreRotationSlot.objects.create(chore=chore, member=sam, order=1)

    ordered_members = list(chore.rotation_members.order_by("chorerotationslot__order"))
    assert ordered_members == [alex, sam]
    assert chore.rotation_current == alex


@pytest.mark.django_db
def test_claimable_chore_starts_unclaimed():
    chore = Chore.objects.create(
        name="Mow the lawn",
        assignment_type=Chore.AssignmentType.CLAIMABLE,
        recurrence_interval_days=14,
        recurrence_weekday=Chore.Weekday.SATURDAY,
    )
    assert chore.current_claim is None


@pytest.mark.django_db
def test_completion_records_who_did_what_and_when():
    alex = Member.objects.create(name="Alex")
    chore = Chore.objects.create(
        name="Water plants",
        assignment_type=Chore.AssignmentType.FIXED,
        recurrence_interval_days=3,
        fixed_assignee=alex,
        last_done=date(2026, 9, 1),
    )
    completion = Completion.objects.create(chore=chore, member=alex)

    assert completion.chore == chore
    assert completion.member == alex
    assert chore.completions.count() == 1
    assert alex.completions.count() == 1
