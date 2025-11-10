from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Event
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.views import APIView
from .models import Event, EventRegistration, EventAttendance
from .serializers import EventSerializer, EventRegistrationSerializer, EventAttendanceSerializer
from accounts.permissions import IsAdminUserRole, IsResidentUserRole
from django.db.models import Q


# ðŸ§‘â€ðŸ’¼ Create Event (Admin Only)
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUserRole])
def create_event(request):
    """Only admins can create events; created_by is set automatically."""
    user = request.user

    serializer = EventSerializer(data=request.data)
    if serializer.is_valid():
        event = serializer.save(created_by=user)  # âœ… auto attach admin
        return Response(EventSerializer(event).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ðŸ“‹ List Events (All users)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_events(request):
    events = Event.objects.select_related('created_by').all().order_by('-date')
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)


# ðŸ” View Single Event
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_detail(request, event_id):
    try:
        event = Event.objects.select_related('created_by').get(id=event_id)
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = EventSerializer(event)
    return Response(serializer.data)


# âœï¸ Update Event (Admin only)
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUserRole])
def update_event(request, event_id):
    user = request.user

    try:
        event = Event.objects.select_related('created_by').get(id=event_id)
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = EventSerializer(event, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# âŒ Delete Event (Admin only)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUserRole])
def delete_event(request, event_id):
    user = request.user

    try:
        event = Event.objects.select_related('created_by').get(id=event_id)
        event.delete()
        return Response({"message": "Event deleted successfully"}, status=status.HTTP_200_OK)
    except Event.DoesNotExist:
        return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

# ðŸ§‘â€ðŸ¤â€ðŸ§‘ Register for event (Resident)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsResidentUserRole])
def register_for_event(request, event_id):
    user = request.user

    try:
        event = Event.objects.select_related('created_by').get(id=event_id)
    except Event.DoesNotExist:
        return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

    # Registration window and capacity checks
    now = timezone.now()
    if event.registration_open and now < event.registration_open:
        return Response({"error": "Registration not yet open."}, status=status.HTTP_403_FORBIDDEN)
    if event.registration_close and now > event.registration_close:
        return Response({"error": "Registration closed."}, status=status.HTTP_403_FORBIDDEN)
    if event.capacity is not None:
        current = EventRegistration.objects.filter(event=event).count()
        if current >= event.capacity:
            return Response({"error": "Event is at full capacity."}, status=status.HTTP_403_FORBIDDEN)

    registration, created = EventRegistration.objects.get_or_create(event=event, resident=user)
    if not created:
        return Response({"message": "You are already registered for this event."}, status=status.HTTP_200_OK)

    serializer = EventRegistrationSerializer(registration)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# Unregister from event (Resident)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsResidentUserRole])
def unregister_for_event(request, event_id):
    user = request.user
    try:
        event = Event.objects.select_related('created_by').get(id=event_id)
    except Event.DoesNotExist:
        return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

    # Prevent unregistering after attendance or after close
    now = timezone.now()
    if event.registration_close and now > event.registration_close:
        return Response({"error": "Registration closed; cannot unregister."}, status=status.HTTP_403_FORBIDDEN)

    registration = EventRegistration.objects.filter(event=event, resident=user).first()
    if not registration:
        return Response({"message": "You are not registered for this event."}, status=status.HTTP_200_OK)

    if hasattr(registration, 'attendance'):
        return Response({"error": "Already checked in; cannot unregister."}, status=status.HTTP_403_FORBIDDEN)

    registration.delete()
    return Response({"message": "Unregistered from event."}, status=status.HTTP_200_OK)


# ðŸ“‹ View all my registered events (Resident)
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsResidentUserRole])
def my_registered_events(request):
    """
    Show all events where the logged-in resident is registered.
    """
    user = request.user

    # role check enforced by permission

    registrations = EventRegistration.objects.filter(resident=user).select_related('event')
    serializer = EventRegistrationSerializer(registrations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Admin: View registrants for an event
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUserRole])
def view_event_registrants(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)

    registrations = (
        EventRegistration.objects
        .select_related('resident', 'event')
        .filter(event=event)
    )
    serializer = EventRegistrationSerializer(registrations, many=True)
    return Response(serializer.data)


# Admin: Mark attendance (via registration_id or barangay_id/username + event_id)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUserRole])
def mark_attendance(request):
    user = request.user
    registration_id = request.data.get('registration_id')
    barangay_id = request.data.get('barangay_id')
    username = request.data.get('username')
    event_id = request.data.get('event_id')

    registration = None

    if registration_id:
        registration = EventRegistration.objects.filter(id=registration_id).first()
    elif barangay_id and event_id:
        registration = EventRegistration.objects.filter(
            resident__profile__barangay_id=barangay_id,
            event_id=event_id,
        ).first()
    elif username and event_id:
        registration = EventRegistration.objects.filter(
            resident__username=username,
            event_id=event_id,
        ).first()
    else:
        return Response(
            {"error": "Provide event_id and barangay_id or username."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not registration:
        return Response({"error": "Registration not found."}, status=status.HTTP_404_NOT_FOUND)
    if hasattr(registration, 'attendance'):
        return Response({"message": "Resident already checked in."}, status=status.HTTP_200_OK)

    attendance = EventAttendance.objects.create(
        registration=registration,
        verified_by=user,
    )
    serializer = EventAttendanceSerializer(attendance)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# Paginated attendance for a specific event
class EventAttendanceByEventView(generics.ListAPIView):
    serializer_class = EventAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

    def get_queryset(self):
        event_id = self.kwargs.get('id')
        return (
            EventAttendance.objects.select_related(
                'registration', 'registration__resident', 'registration__event', 'verified_by'
            )
            .filter(registration__event_id=event_id)
            .order_by('-checked_in_at')
        )


# Paginated list of all events
class EventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Event.objects.select_related('created_by').all()
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(event_type__icontains=q)
                | Q(venue__icontains=q)
                | Q(description__icontains=q)
            )
        ordering = self.request.query_params.get('ordering')
        ordering_map = {
            'date': 'date',
            '-date': '-date',
            'title': 'title',
            '-title': '-title',
        }
        order = ordering_map.get(ordering, '-date')
        return qs.order_by(order)


# Retrieve single event (by id)
class EventDetailView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'


# Registrations for a specific event (admin)
class EventRegistrationsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

    def get(self, request, id):
        registrations = EventRegistration.objects.select_related('resident', 'event').filter(event_id=id)
        serializer = EventRegistrationSerializer(registrations, many=True)
        return Response(serializer.data)


# Paginated list of all attendance (admin)
class EventAttendanceListView(generics.ListAPIView):
    serializer_class = EventAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

    def get_queryset(self):
        return (
            EventAttendance.objects.select_related(
                'registration', 'registration__resident', 'registration__event', 'verified_by'
            ).order_by('-checked_in_at')
        )







