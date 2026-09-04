from django.db import models
from django.utils import timezone


class Member(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Chore(models.Model):
    class AssignmentType(models.TextChoices):
        FIXED = "fixed", "Fixed"
        ROTATING = "rotating", "Rotating"
        CLAIMABLE = "claimable", "Claimable"

    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    name = models.CharField(max_length=200)
    assignment_type = models.CharField(max_length=10, choices=AssignmentType.choices)

    # Recurrence rule: an interval in days, optionally anchored to a weekday.
    # e.g. interval=1 -> daily, interval=3 -> "every 3 days",
    # interval=14 + weekday=Monday -> "every other Monday".
    recurrence_interval_days = models.PositiveIntegerField(
        help_text="Days between occurrences, e.g. 3 for 'every 3 days', "
        "14 for 'every other <weekday>'."
    )
    recurrence_weekday = models.IntegerField(
        choices=Weekday.choices,
        null=True,
        blank=True,
        help_text="Optional anchor weekday, e.g. Monday for 'every other Monday'.",
    )

    last_done = models.DateField(null=True, blank=True)
    next_due = models.DateField(null=True, blank=True)

    # Fixed assignment: chore always belongs to this member.
    fixed_assignee = models.ForeignKey(
        Member,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="fixed_chores",
    )

    # Rotating assignment: cycles through an ordered set of members.
    rotation_members = models.ManyToManyField(
        Member,
        through="ChoreRotationSlot",
        related_name="rotating_chores",
        blank=True,
    )
    rotation_current = models.ForeignKey(
        Member,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="chores_up_next",
        help_text="Member whose turn it is next, for rotating chores.",
    )

    # Claimable assignment: sits in a shared pool until someone claims it.
    current_claim = models.ForeignKey(
        Member,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="claimed_chores",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ChoreRotationSlot(models.Model):
    """One position in a rotating chore's ordered cycle of members."""

    chore = models.ForeignKey(Chore, on_delete=models.CASCADE, related_name="rotation_slots")
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(fields=["chore", "order"], name="unique_chore_rotation_order"),
            models.UniqueConstraint(fields=["chore", "member"], name="unique_chore_rotation_member"),
        ]

    def __str__(self):
        return f"{self.chore} -> {self.member} (#{self.order})"


class Completion(models.Model):
    """Append-only log entry: a member marked a chore done at a point in time."""

    chore = models.ForeignKey(Chore, on_delete=models.CASCADE, related_name="completions")
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="completions")
    done_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-done_at"]

    def __str__(self):
        return f"{self.member} completed {self.chore} at {self.done_at:%Y-%m-%d %H:%M}"
