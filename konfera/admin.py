from django.contrib import admin

from konfera.models import (Receipt, Order, Location, Event, Sponsor,
                            TicketType, DiscountCodes, Ticket, Speaker,
                            Talk, Room, Schedule)

admin.site.register(Receipt)
admin.site.register(Order)
admin.site.register(Location)
admin.site.register(Event)
admin.site.register(Sponsor)
admin.site.register(TicketType)
admin.site.register(DiscountCodes)
admin.site.register(Ticket)
admin.site.register(Speaker)
admin.site.register(Talk)
admin.site.register(Room)
admin.site.register(Schedule)
