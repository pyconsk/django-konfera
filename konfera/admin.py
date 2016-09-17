from django.contrib import admin

from konfera.models import (Receipt, Order, Location, Event, Sponsor, TicketType, DiscountCode, Ticket, Speaker, Talk,
                            Room, Schedule)


class SponsorshipInline(admin.TabularInline):
    model = Event.sponsors.through
    extra = 1


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_from', 'date_to', 'event_type', 'status')
    list_filter = ('event_type', 'status')

    fieldsets = (
        ('Description', {
            'fields': ('title', 'slug', 'description'),
        }),
        ('Dates', {
            'fields': ('date_from', 'date_to'),
        }),
        ('Details', {
            'fields': ('event_type', 'status', 'location'),
        }),
    )

    inlines = [
        SponsorshipInline,
    ]

    prepopulated_fields = {
        'slug': ('title',),
    }

admin.site.register(Event, EventAdmin)


admin.site.register(Receipt)
admin.site.register(Order)
admin.site.register(Location)
admin.site.register(Sponsor)
admin.site.register(TicketType)
admin.site.register(DiscountCode)
admin.site.register(Ticket)
admin.site.register(Speaker)
admin.site.register(Talk)
admin.site.register(Room)
admin.site.register(Schedule)
