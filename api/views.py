from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import User, Event, Registration
from .serializers import EventSerializer, RegistrationSerializer
import requests

# External API authentication endpoint (example)
EXTERNAL_API_AUTH_URL = ""

# User authentication view
class UserLoginView(APIView):
    def post(self, request):
        # Send data to external API for authentication
        external_auth_data = {
            'email': request.data.get('email'),
            'password': request.data.get('password'),
        }
        response = requests.post(EXTERNAL_API_AUTH_URL, json=external_auth_data)

        if response.status_code == 200:
            auth_data = response.json()
            # Create or update user
            user, created = User.objects.update_or_create(
                external_id=auth_data['external_id'],
                defaults={
                    'name': auth_data['name'],
                    'email': auth_data['email']
                }
            )
            return Response({
                'message': 'Authentication successful',
                'user': auth_data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Authentication failed'
            }, status=status.HTTP_401_UNAUTHORIZED)

# View to list upcoming events
class EventListView(APIView):
    def get(self, request):
        # Fetch upcoming and open events
        now = timezone.now()
        events = Event.objects.filter(start_time__gte=now, is_public=True)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Event registration view
class EventRegisterView(APIView):
    def post(self, request, event_id):
        user_id = request.data.get('user_id')

        # Fetch user and event
        try:
            user = User.objects.get(pk=user_id)
            event = Event.objects.get(pk=event_id)
        except (User.DoesNotExist, Event.DoesNotExist):
            return Response({
                'error': 'User or Event not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Register user for the event
        registration, created = Registration.objects.get_or_create(user=user, event=event)

        if created:
            return Response({
                'message': 'User successfully registered for the event'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': 'User already registered for the event'
            }, status=status.HTTP_400_BAD_REQUEST)

# View to list user registrations
class UserRegistrationsView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

        registrations = Registration.objects.filter(user=user)
        serializer = RegistrationSerializer(registrations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
