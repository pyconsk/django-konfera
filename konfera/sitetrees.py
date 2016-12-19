from sitetree.utils import tree, item

sitetrees = (
    tree('events', items=[
        item('Venue', 'event_venue event.slug'),
        item('Tickets', 'event_tickets event.slug'),
        item('Call for Proposals', 'event_cfp_form event.slug'),
        item('Code of Conduct', 'event_coc event.slug'),
    ]),
)
