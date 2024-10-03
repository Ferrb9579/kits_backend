from rest_framework import serializers
from .models import Event, User, Registration, Department, Attendance, AttendanceSession

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_faculty', 'department', 'register_id']

class AttendanceSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceSession
        fields = ['id', 'name', 'created_at']

class EventSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    allowed_departments = DepartmentSerializer(many=True, read_only=True)
    attendance_sessions = AttendanceSessionSerializer(source='event_attendance_sessions', many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'start_time', 'end_time', 'location', 
                  'created_at', 'updated_at', 'is_public', 'created_by', 'allowed_departments', 
                  'attendance_sessions', 'registration_open', 'available_slots']

class RegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)

    class Meta:
        model = Registration
        fields = ['id', 'user', 'event', 'status', 'registered_at']

class AttendanceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    session = AttendanceSessionSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'user', 'event', 'session', 'is_present', 'was_registered']
