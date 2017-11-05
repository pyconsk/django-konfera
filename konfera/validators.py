from django.core.exceptions import ValidationError

from konfera.models import Event, TicketType


def event_uuid_validator(value):
    """Check value is a valid uuid for an existing event"""
    try:
        Event.objects.get(uuid=value)
    except Event.DoesNotExist:
        raise ValidationError('Event with uuid {} not found.'.format(value))


def aid_ticket_type_uuid_validator(value):
    """Check value is a valid uuid for an existing ticket type"""
    try:
        TicketType.objects.get(uuid=value, attendee_type=TicketType.AID)
    except TicketType.DoesNotExist:
        raise ValidationError('Aid ticket type with uuid {} not found.'.format(value))
