from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import User, Event, Registration, Attendance, AttendanceSession
from .serializers import EventSerializer, RegistrationSerializer, AttendanceSerializer, AttendanceSessionSerializer
import requests

EXTERNAL_API_AUTH_URL = "http://127.0.0.1:3000/auth"

class EventCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not request.user.is_faculty:
            return Response({'error': 'Only faculty members can create events'}, status=status.HTTP_403_FORBIDDEN)

        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save(created_by=request.user)
            allowed_departments = request.data.get('allowed_departments', [])
            event.allowed_departments.set(allowed_departments)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventRegisterView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)

        if not event.registration_open:
            return Response({'error': 'Registration for this event is closed'}, status=status.HTTP_400_BAD_REQUEST)

        if event.allowed_departments.exists() and request.user.department not in event.allowed_departments.all():
            return Response({'error': 'You are not allowed to register for this event'}, status=status.HTTP_403_FORBIDDEN)

        if event.available_slots <= 0:
            return Response({'error': 'No available slots for this event'}, status=status.HTTP_400_BAD_REQUEST)

        registration, created = Registration.objects.get_or_create(user=request.user, event=event)

        if created:
            event.available_slots -= 1
            event.save()
            if event.available_slots == 0:
                event.registration_open = False
                event.save()
            return Response({'message': 'Successfully registered for the event'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Already registered for this event'}, status=status.HTTP_400_BAD_REQUEST)

class EventRegisteredStudentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        registrations = Registration.objects.filter(event=event)
        serializer = RegistrationSerializer(registrations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class EventCloseRegistrationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)

        if request.user != event.created_by:
            return Response({'error': 'Only the event creator can close registration'}, status=status.HTTP_403_FORBIDDEN)

        event.registration_open = False
        event.save()
        return Response({'message': 'Event registration closed successfully'}, status=status.HTTP_200_OK)

class EventListView(APIView):
    def get(self, request):
        now = timezone.now()
        events = Event.objects.filter(start_time__gte=now, is_public=True)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserLoginView(APIView):
    def post(self, request):
        print(request.data)
        external_auth_data = {
            'email': request.data.get('email'),
            'password': request.data.get('password'),
        }
        response = requests.post(EXTERNAL_API_AUTH_URL, json=external_auth_data)
        print(response.text)

        if response.status_code == 200:
            auth_data = {
                "name": "Fanisus",
                "email": "fanisusr@karunya.edu.in",
                "register_id": "12345"
            }
            user, created = User.objects.update_or_create(
                register_id=auth_data['register_id'],
                defaults={
                    'username': auth_data['name'],
                    'email': auth_data['email'],
                    'name': auth_data['name']
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

class AttendanceSessionCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)

        if request.user != event.created_by:
            return Response({'error': 'Only the event creator can create attendance sessions'}, status=status.HTTP_403_FORBIDDEN)

        serializer = AttendanceSessionSerializer(data=request.data)
        if serializer.is_valid():
            session = serializer.save(event=event)
            # Append the session ID to the event's attendance_sessions list
            event.attendance_sessions.append(session.id)
            event.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AttendanceRecordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)

        if request.user != event.created_by:
            return Response({'error': 'Only the event creator can record attendance'}, status=status.HTTP_403_FORBIDDEN)

        session_id = request.data.get('session_id')  # Now using session_id
        register_id = request.data.get('register_id')
        is_present = request.data.get('is_present', False)

        user = get_object_or_404(User, register_id=register_id)
        was_registered = Registration.objects.filter(user=user, event=event).exists()

        attendance, created = Attendance.objects.get_or_create(
            user=user,
            event=event,
            session_id=session_id,
            defaults={'is_present': is_present, 'was_registered': was_registered}
        )

        if not created:
            attendance.is_present = is_present
            attendance.save()

        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AttendanceListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)

        if request.user != event.created_by:
            return Response({'error': 'Only the event creator can view attendance'}, status=status.HTTP_403_FORBIDDEN)

        attendances = Attendance.objects.filter(event=event)
        serializer = AttendanceSerializer(attendances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
