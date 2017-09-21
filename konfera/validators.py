from django.core.exceptions import ValidationError

from konfera.models import Event


def event_uuid_validator(value):
    """Check value is a valid uuid for an existing event"""
    try:
        Event.objects.get(uuid=value)
    except Event.DoesNotExist:
        raise ValidationError('Event with uuid {} not found.'.format(value))
