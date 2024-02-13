from django.urls import path
from .views import *

urlpatterns = [
    path('signup/', signup, name='signup_form'),
    path('signup_success/', signup_success, name='signup_success'),
    path('events/', list_events, name='list_events'),
    path('events/register/<int:event_id>', register_for_event, name='register_for_event'),
    path('events/discard/<int:event_id>', discard_event, name='discard_event'),
    path('events/add', add_event),
    path('events/past_events/', list_past_events, name='list_past_events'),
    path('events/view/<int:event_id>', view_event, name='view_event'),
    path('availability_times/', list_availability),
    path('availability_success/', availability_success, name='availability_success'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('employees/', list_employees),
    path('users/', list_users),
    path('delete_employees/', delete_employees),
]
