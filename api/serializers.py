from rest_framework import serializers
from .models import Event, User, Registration, Department, AttendanceSession, Attendance

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_faculty', 'department']

class EventSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    allowed_departments = DepartmentSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = '__all__'

class RegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)

    class Meta:
        model = Registration
        fields = ['id', 'user', 'event', 'status', 'registered_at']

class AttendanceSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceSession
        fields = ['id', 'event', 'name', 'created_at']

class AttendanceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'session', 'user', 'is_present', 'was_registered']