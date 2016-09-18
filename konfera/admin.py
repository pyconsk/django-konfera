from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

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


class TalkAdmin(admin.ModelAdmin):
    list_display = ('title', 'primary_speaker', 'type', 'duration', 'event', 'status',)
    list_filter = ('type', 'duration', 'event', 'status',)
    search_fields = ('=title', '=primary_speaker__first_name', '=primary_speaker__last_name', '=event__title')
    ordering = ('title',)
    fieldsets = (
        (_('Description'), {
            'fields': ('title', 'abstract', 'event',)
        }),
        (_('Details'), {
            'fields': (('type', 'duration',), 'status', ('primary_speaker', 'secondary_speaker',),)
        }),
    )


admin.site.register(Receipt)
admin.site.register(Order)
admin.site.register(Location)
admin.site.register(Sponsor)
admin.site.register(TicketType)
admin.site.register(DiscountCode)
admin.site.register(Ticket)
admin.site.register(Speaker, SpeakerAdmin)
admin.site.register(Talk, TalkAdmin)
admin.site.register(Room)
admin.site.register(Schedule)
