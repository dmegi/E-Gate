from django.urls import path
from . import views

urlpatterns = [
    # 🧩 Core Event Endpoints
    path('', views.list_events, name='list_events'),
    path('create/', views.create_event, name='create_event'),
    path('<int:event_id>/', views.event_detail, name='event_detail'),
    path('update/<int:event_id>/', views.update_event, name='update_event'),
    path('delete/<int:event_id>/', views.delete_event, name='delete_event'),

    # 🧾 Resident Event Registration
    path('<int:event_id>/register/', views.register_for_event, name='register_for_event'),
    path('<int:event_id>/unregister/', views.unregister_for_event, name='unregister_for_event'),
    path('my-registrations/', views.my_registered_events, name='my_registered_events'),

    # 👥 Admin: View registrants & mark attendance
    path('<int:event_id>/registrants/', views.view_event_registrants, name='view_event_registrants'),
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),

    # 📊 Class-based (APIView) Endpoints
    path('attendance/all/', views.EventAttendanceListView.as_view(), name='attendance_list'),
    path('list/', views.EventListView.as_view(), name='event_list'),
    path('<int:id>/detail/', views.EventDetailView.as_view(), name='event_detail_view'),
    path('<int:id>/registrations/', views.EventRegistrationsView.as_view(), name='event_registrations'),
    path('<int:id>/attendance/', views.EventAttendanceByEventView.as_view(), name='event_attendance_by_event'),
]
