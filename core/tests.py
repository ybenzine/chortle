from datetime import date

import pytest
from django.urls import reverse

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


# --- Member CRUD views ---


@pytest.mark.django_db
def test_member_list_shows_members_ordered_by_name(client):
    Member.objects.create(name="Zoe")
    Member.objects.create(name="Alex")

    response = client.get(reverse("core:member-list"))

    assert response.status_code == 200
    names = [m.name for m in response.context["members"]]
    assert names == ["Alex", "Zoe"]


@pytest.mark.django_db
def test_member_list_shows_empty_state_message(client):
    response = client.get(reverse("core:member-list"))

    assert response.status_code == 200
    assert b"No members yet" in response.content


@pytest.mark.django_db
def test_add_member_with_valid_name_creates_member_and_redirects_to_list(client):
    response = client.post(reverse("core:member-add"), {"name": "Alex"})

    assert response.status_code == 302
    assert response.url == reverse("core:member-list")
    assert Member.objects.filter(name="Alex").exists()

    list_response = client.get(reverse("core:member-list"))
    assert b"Alex" in list_response.content


@pytest.mark.django_db
def test_add_member_with_empty_name_reshows_form_with_error(client):
    response = client.post(reverse("core:member-add"), {"name": ""})

    assert response.status_code == 200
    assert response.context["form"].errors
    assert Member.objects.count() == 0


@pytest.mark.django_db
def test_add_member_with_duplicate_name_reshows_form_with_error(client):
    Member.objects.create(name="Alex")

    response = client.post(reverse("core:member-add"), {"name": "Alex"})

    assert response.status_code == 200
    assert response.context["form"].errors
    assert Member.objects.filter(name="Alex").count() == 1


@pytest.mark.django_db
def test_edit_member_form_is_prefilled_with_current_name(client):
    member = Member.objects.create(name="Alex")

    response = client.get(reverse("core:member-edit", args=[member.pk]))

    assert response.status_code == 200
    assert response.context["form"].initial["name"] == "Alex"


@pytest.mark.django_db
def test_edit_member_with_valid_name_updates_same_record(client):
    member = Member.objects.create(name="Alex")

    response = client.post(reverse("core:member-edit", args=[member.pk]), {"name": "Alexandra"})

    assert response.status_code == 302
    assert response.url == reverse("core:member-list")
    assert Member.objects.count() == 1
    member.refresh_from_db()
    assert member.name == "Alexandra"


@pytest.mark.django_db
def test_edit_member_with_another_members_name_reshows_form_with_error(client):
    Member.objects.create(name="Alex")
    sam = Member.objects.create(name="Sam")

    response = client.post(reverse("core:member-edit", args=[sam.pk]), {"name": "Alex"})

    assert response.status_code == 200
    assert response.context["form"].errors
    sam.refresh_from_db()
    assert sam.name == "Sam"


@pytest.mark.django_db
def test_edit_member_with_empty_name_reshows_form_with_error(client):
    member = Member.objects.create(name="Alex")

    response = client.post(reverse("core:member-edit", args=[member.pk]), {"name": ""})

    assert response.status_code == 200
    assert response.context["form"].errors
    member.refresh_from_db()
    assert member.name == "Alex"


@pytest.mark.django_db
def test_delete_member_get_shows_confirmation_and_does_not_delete(client):
    member = Member.objects.create(name="Alex")

    response = client.get(reverse("core:member-delete", args=[member.pk]))

    assert response.status_code == 200
    assert Member.objects.filter(pk=member.pk).exists()


@pytest.mark.django_db
def test_delete_member_confirmation_warns_about_related_chores_and_completions(client):
    alex = Member.objects.create(name="Alex")
    sam = Member.objects.create(name="Sam")
    fixed_chore = Chore.objects.create(
        name="Take out trash",
        assignment_type=Chore.AssignmentType.FIXED,
        recurrence_interval_days=7,
        fixed_assignee=alex,
    )
    rotating_chore = Chore.objects.create(
        name="Wash dishes",
        assignment_type=Chore.AssignmentType.ROTATING,
        recurrence_interval_days=1,
        rotation_current=alex,
    )
    ChoreRotationSlot.objects.create(chore=rotating_chore, member=alex, order=0)
    ChoreRotationSlot.objects.create(chore=rotating_chore, member=sam, order=1)
    claimable_chore = Chore.objects.create(
        name="Mow the lawn",
        assignment_type=Chore.AssignmentType.CLAIMABLE,
        recurrence_interval_days=14,
        current_claim=alex,
    )
    Completion.objects.create(chore=fixed_chore, member=alex)

    response = client.get(reverse("core:member-delete", args=[alex.pk]))

    assert response.status_code == 200
    affected_names = {c.name for c in response.context["affected_chores"]}
    assert affected_names == {fixed_chore.name, rotating_chore.name, claimable_chore.name}
    assert response.context["completions_count"] == 1
    assert b"unassigned" in response.content
    assert b"rotation slot" in response.content
    assert b"completion history" in response.content


@pytest.mark.django_db
def test_delete_member_confirmation_with_no_relations_says_so(client):
    member = Member.objects.create(name="Alex")

    response = client.get(reverse("core:member-delete", args=[member.pk]))

    assert response.status_code == 200
    assert not response.context["affected_chores"]
    assert response.context["completions_count"] == 0
    assert b"no related chores or completion history" in response.content


@pytest.mark.django_db
def test_confirming_delete_removes_member_and_redirects_with_success_message(client):
    member = Member.objects.create(name="Alex")

    response = client.post(reverse("core:member-delete", args=[member.pk]), follow=True)

    assert response.status_code == 200
    assert not Member.objects.filter(pk=member.pk).exists()
    messages = [str(m) for m in response.context["messages"]]
    assert any("Removed" in m for m in messages)
    assert reverse("core:member-edit", args=[member.pk]).encode() not in response.content


@pytest.mark.django_db
def test_confirming_delete_clears_relations_per_on_delete_behavior(client):
    alex = Member.objects.create(name="Alex")
    sam = Member.objects.create(name="Sam")
    fixed_chore = Chore.objects.create(
        name="Take out trash",
        assignment_type=Chore.AssignmentType.FIXED,
        recurrence_interval_days=7,
        fixed_assignee=alex,
    )
    rotating_chore = Chore.objects.create(
        name="Wash dishes",
        assignment_type=Chore.AssignmentType.ROTATING,
        recurrence_interval_days=1,
        rotation_current=alex,
    )
    ChoreRotationSlot.objects.create(chore=rotating_chore, member=alex, order=0)
    ChoreRotationSlot.objects.create(chore=rotating_chore, member=sam, order=1)
    Completion.objects.create(chore=fixed_chore, member=alex)

    client.post(reverse("core:member-delete", args=[alex.pk]))

    fixed_chore.refresh_from_db()
    rotating_chore.refresh_from_db()
    assert fixed_chore.fixed_assignee is None
    assert rotating_chore.rotation_current is None
    assert not ChoreRotationSlot.objects.filter(chore=rotating_chore, member_id=alex.pk).exists()
    assert Completion.objects.filter(member_id=alex.pk).count() == 0
    # The other rotation member's slot is untouched.
    assert ChoreRotationSlot.objects.filter(chore=rotating_chore, member=sam).exists()


@pytest.mark.django_db
def test_edit_member_for_missing_id_returns_404(client):
    response = client.get(reverse("core:member-edit", args=[999999]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_member_for_missing_id_returns_404(client):
    response = client.get(reverse("core:member-delete", args=[999999]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_member_list_links_to_add_edit_delete(client):
    member = Member.objects.create(name="Alex")

    response = client.get(reverse("core:member-list"))
    content = response.content.decode()

    assert reverse("core:member-add") in content
    assert reverse("core:member-edit", args=[member.pk]) in content
    assert reverse("core:member-delete", args=[member.pk]) in content
