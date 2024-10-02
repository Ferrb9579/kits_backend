from rest_framework import serializers
from .models import Event, User, Registration

# Serializer for Event model
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

# Serializer for User model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'email', 'external_id']

# Serializer for Registration model
class RegistrationSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    
    class Meta:
        model = Registration
        fields = ['event', 'status', 'registered_at']
