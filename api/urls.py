from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.UserLoginView.as_view(), name='login'),

    # Events
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/create/', views.EventCreateView.as_view(), name='event_create'),
    path('events/<int:event_id>/register/', views.EventRegisterView.as_view(), name='event_register'),
    path('events/<int:event_id>/registered-students/', views.EventRegisteredStudentsView.as_view(), name='event_registered_students'),
    path('events/<int:event_id>/close-registration/', views.EventCloseRegistrationView.as_view(), name='event_close_registration'),

    # Attendance Sessions
    path('events/<int:event_id>/create-attendance-session/', views.AttendanceSessionCreateView.as_view(), name='create_attendance_session'),

    # Attendance
    path('attendance-sessions/<int:session_id>/record/', views.AttendanceRecordView.as_view(), name='record_attendance'),
    path('events/<int:event_id>/attendance-list/', views.AttendanceListView.as_view(), name='list_attendance'),
]
