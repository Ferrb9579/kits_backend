from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class User(AbstractUser):
    register_id = models.CharField(max_length=100, unique=True)
    is_faculty = models.BooleanField(default=False)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username

class Event(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(max_length=4096)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=512, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    allowed_departments = models.ManyToManyField(Department, blank=True)
    registration_open = models.BooleanField(default=True)
    available_slots = models.PositiveIntegerField(default=0)
    attendance_sessions = models.JSONField(default=list)  # Stores session IDs as JSON list

    def __str__(self):
        return self.title

class Registration(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='registered')
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    session_id = models.IntegerField()  # Track attendance by session ID
    created_at = models.DateTimeField(auto_now_add=True)
    is_present = models.BooleanField(default=False)
    was_registered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.event.title} - Session {self.session_id}"

    class Meta:
        unique_together = ('user', 'event', 'session_id')  # Ensures unique attendance for a session

# Optional helper model if you still need session-specific names or data
class AttendanceSession(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_attendance_sessions')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event.title} - {self.name}"
