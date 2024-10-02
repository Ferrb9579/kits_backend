from django.urls import path
from . import views
urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/<int:event_id>/register/', views.EventRegisterView.as_view(), name='event_register'),
    path('users/<int:user_id>/registrations/', views.UserRegistrationsView.as_view(), name='user_registrations'),
]
