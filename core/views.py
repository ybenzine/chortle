from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MemberForm
from .models import Chore, Member


def member_list(request):
    members = Member.objects.all()
    return render(request, "core/member_list.html", {"members": members})


def member_add(request):
    if request.method == "POST":
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            messages.success(request, f'Added "{member.name}".')
            return redirect("core:member-list")
    else:
        form = MemberForm()
    return render(request, "core/member_form.html", {"form": form, "title": "Add member"})


def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == "POST":
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated "{member.name}".')
            return redirect("core:member-list")
    else:
        form = MemberForm(instance=member)
    return render(
        request,
        "core/member_form.html",
        {"form": form, "title": "Edit member", "member": member},
    )


def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    affected_chores = Chore.objects.filter(
        Q(fixed_assignee=member)
        | Q(rotation_members=member)
        | Q(rotation_current=member)
        | Q(current_claim=member)
    ).distinct()
    completions_count = member.completions.count()

    if request.method == "POST":
        name = member.name
        member.delete()
        messages.success(request, f'Removed "{name}".')
        return redirect("core:member-list")

    return render(
        request,
        "core/member_confirm_delete.html",
        {
            "member": member,
            "affected_chores": affected_chores,
            "completions_count": completions_count,
        },
    )
