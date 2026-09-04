from django.contrib import admin

from .models import Chore, ChoreRotationSlot, Completion, Member


class ChoreRotationSlotInline(admin.TabularInline):
    model = ChoreRotationSlot
    extra = 1


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "assignment_type",
        "fixed_assignee",
        "rotation_current",
        "current_claim",
        "last_done",
        "next_due",
    )
    list_filter = ("assignment_type",)
    search_fields = ("name",)
    inlines = [ChoreRotationSlotInline]


@admin.register(Completion)
class CompletionAdmin(admin.ModelAdmin):
    list_display = ("chore", "member", "done_at")
    list_filter = ("chore", "member")
    date_hierarchy = "done_at"
