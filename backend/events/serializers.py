from rest_framework import serializers
from .models import Event, EventRegistration, EventAttendance


# 🧩 Event Serializer
class EventSerializer(serializers.ModelSerializer):
    # Show username instead of raw user id
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id',
            'title',
            'description',
            'event_type',
            'date',
            'venue',
            'capacity',
            'registration_open',
            'registration_close',
            'status',
            'created_by',
            'created_at'
        ]
        read_only_fields = ['created_by', 'created_at']

    def validate_event_type(self, value):
        """Make event_type case-insensitive."""
        return value.lower()

    def validate(self, attrs):
        from django.utils import timezone
        date = attrs.get('date', getattr(self.instance, 'date', None))
        reg_open = attrs.get('registration_open', getattr(self.instance, 'registration_open', None))
        reg_close = attrs.get('registration_close', getattr(self.instance, 'registration_close', None))
        capacity = attrs.get('capacity', getattr(self.instance, 'capacity', None))

        if capacity is not None and capacity < 0:
            raise serializers.ValidationError({ 'capacity': 'Capacity must be >= 0.' })
        if reg_open and reg_close and reg_open > reg_close:
            raise serializers.ValidationError({ 'registration_open': 'Open must be before close.' })
        if date and reg_close and reg_close > date:
            raise serializers.ValidationError({ 'registration_close': 'Close cannot be after event date.' })
        if date and date < timezone.now():
            raise serializers.ValidationError({ 'date': 'Event date must be in the future.' })
        return attrs

# 🧩 Event Registration Serializer
class EventRegistrationSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='event.title', read_only=True)
    resident_username = serializers.CharField(source='resident.username', read_only=True)

    class Meta:
        model = EventRegistration
        fields = [
            'id',
            'event',
            'event_title',
            'resident',
            'resident_username',
            'registered_at',
            'attendance_confirmed'
        ]
        # event/resident are set server-side in views; keep them read-only
        read_only_fields = ['registered_at', 'attendance_confirmed', 'event', 'resident']


# 🧩 Event Attendance Serializer
class EventAttendanceSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(source='registration.event.title', read_only=True)
    event_id = serializers.IntegerField(source='registration.event.id', read_only=True)
    resident_username = serializers.CharField(source='registration.resident.username', read_only=True)
    verified_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = EventAttendance
        fields = [
            'id',
            'event_id',
            'event_title',
            'resident_username',
            'checked_in_at',
            'verified_by'
        ]
        read_only_fields = ['checked_in_at', 'verified_by']
