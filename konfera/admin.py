from django.contrib import admin

from konfera.models import (Receipt, Order, Location, Event, Sponsor,
                            TicketType, DiscountCode, Ticket, Speaker,
                            Talk, Room, Schedule)


class EventAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Receipt)
admin.site.register(Order)
admin.site.register(Location)
admin.site.register(Event, EventAdmin)
admin.site.register(Sponsor)
admin.site.register(TicketType)
admin.site.register(DiscountCode)
admin.site.register(Ticket)
admin.site.register(Speaker)
admin.site.register(Talk)
admin.site.register(Room)
admin.site.register(Schedule)
