EVENT_TYPE_CHOICES = (
    ('conference', ('Conference')),
    ('meetup', ('Meetup')),
)

EVENT_STATUS_CHOICES = (
    ('draft', ('Draft')),
    ('published', ('Published')),
    ('private', ('Private')),
    ('expired', ('Expired')),
)
ORDER_CHOICES = (
    ('awaiting_payment', ('Awaiting payment')),
    ('paid', ('Partly paid')),
    ('partly_paid', ('Paid')),
    ('expired', ('Expired')),
    ('cancelled', ('Cancelled')),
)

TITLE_CHOICES = (
    ('none', ''),
    ('mr', ('Mr.')),
    ('ms', ('Ms.')),
)

SPONSOR_TYPE = (
    (1, ('Platinum')),
    (2, ('Gold')),
    (3, ('Silver')),
    (4, ('Bronze')),
    (5, ('Other')),
    (6, ('Django girls')),
)
TALK_STATUS = (
    ('cfp', ('Call For Proposals')),
    ('draft', ('Draft')),
    ('approved', ('Approved')),
    ('rejected', ('Rejected')),
    ('withdrawn', ('Withdrawn')),
)

TALK_TYPE = (
    ('talk', ('Talk')),
    ('workshop', ('Workshop')),
)

TALK_DURATION = (
    (5, ('5 min')),
    (30, ('30 min')),
    (45, ('45 min')),
)

TICKET_STATUS = (
    ('requested', ('Requested')),
    ('registered', ('Registered')),
    ('checked-in', ('Checked-in')),
    ('cancelled', ('Cancelled')),
)
TICKET_TYPE_CHOICES = (
    ('volunteer', ('Volunteer')),
    ('press', ('Press')),
    ('student', ('Student')),
    ('attendee', ('Attendee')),
    ('supporter', ('Supporter')),
    ('speaker', ('Speaker')),
    ('sponsor', ('Sponsor')),
    ('aid', ('Aid')),
)

ACCESSIBILITY = (
    ('public', ('Public')),
    ('private', ('Private')),
    ('disabled', ('Disabled')),
)
STATUSES = (
    ('na', ('Not available yet')),
    ('active', ('Active')),
    ('expired', ('Expired')),
)
