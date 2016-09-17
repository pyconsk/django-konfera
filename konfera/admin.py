from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from konfera.models import (Receipt, Order, Location, Event, Sponsor,
                            TicketType, DiscountCode, Ticket, Speaker,
                            Talk, Room, Schedule)


class EventAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'country', 'social_url',)
    list_filter = ('country', 'title', 'sponsor',)
    ordering = ('last_name', 'first_name',)
    search_fields = ('=last_name', '=first_name',)  # case insensitive searching
    fieldsets = (
        (_('Name'), {
            'fields': ('title', ('first_name', 'last_name',),)
        }),
        (_('Contact'), {
            'fields': ('email', 'phone',)
        }),
        (_('About'), {
            'fields': ('bio', 'country', ('url', 'social_url',), 'sponsor',)
        }),
    )


admin.site.register(Receipt)
admin.site.register(Order)
admin.site.register(Location)
admin.site.register(Event, EventAdmin)
admin.site.register(Sponsor)
admin.site.register(TicketType)
admin.site.register(DiscountCode)
admin.site.register(Ticket)
admin.site.register(Speaker, SpeakerAdmin)
admin.site.register(Talk)
admin.site.register(Room)
admin.site.register(Schedule)
