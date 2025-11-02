from django.db import models
from residents.models import User


class Event(models.Model):
    EVENT_TYPES = [
        ("medical", "Medical Mission"),
        ("vaccination", "Vaccination Drive"),
        ("assembly", "Barangay Assembly"),
        ("relief", "Disaster Relief"),
        ("community", "Community Event"),
        ("sk_election", "SK Election"),
    ]

    STATUS_CHOICES = [
        ("upcoming", "Upcoming"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    date = models.DateTimeField()
    capacity = models.PositiveIntegerField(null=True, blank=True)
    registration_open = models.DateTimeField(null=True, blank=True)
    registration_close = models.DateTimeField(null=True, blank=True)
    venue = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="upcoming")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_events")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()})"


class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    resident = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="event_registrations",
        null=True,
        blank=True,
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    attendance_confirmed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("event", "resident")

    def __str__(self):
        return f"{self.resident.username} registered for {self.event.title}"


class EventAttendance(models.Model):
    registration = models.OneToOneField(
        "EventRegistration", on_delete=models.CASCADE, related_name="attendance"
    )
    checked_in_at = models.DateTimeField(auto_now_add=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="verified_attendance",
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
            f"Attendance for {self.registration.resident.username} - "
            f"{self.registration.event.title}"
        )
