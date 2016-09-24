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
        (_('Description'), {
            'fields': ('title', 'slug', 'description'),
        }),
        (_('Dates'), {
            'fields': ('date_from', 'date_to'),
        }),
        (_('Details'), {
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

admin.site.register(Speaker, SpeakerAdmin)


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

admin.site.register(Talk, TalkAdmin)


class SponsoredEventsInline(admin.TabularInline):
    # Django 1.8 doesn't allow Sponsor.sponsored_events.through (caused by related_name)
    model = Event.sponsors.through
    verbose_name = _('Sponsored event')
    verbose_name_plural = _('Sponsored events')
    extra = 1


class SponsoredSpeakersInline(admin.StackedInline):
    model = Speaker
    verbose_name = _('Sponsored speaker')
    verbose_name_plural = _('Sponsored speakers')
    extra = 1


class SponsorAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'url',)
    list_filter = ('type',)
    search_fields = ('=title',)
    ordering = ('type', 'title',)
    fieldsets = (
        (None, {
            'fields': ('title', 'type', 'logo', 'url', 'about_us',)
        }),
    )

    inlines = [
        SponsoredEventsInline,
        SponsoredSpeakersInline,
    ]

admin.site.register(Sponsor, SponsorAdmin)


class LocationAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'capacity')
    list_filter = ('city',)
    fieldsets = (
        (_('Details'), {
            'fields': ('title', 'capacity',)
        }),
        (_('Address'), {
            'fields': ('street', 'street2', 'state', 'city', 'postcode',)
        }),
    )

admin.site.register(Location, LocationAdmin)


class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('purchase_date', 'payment_date')

admin.site.register(Order, OrderAdmin)


class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'attendee_type', 'event', 'status')
    list_filter = ('attendee_type',)
    readonly_fields = ('status',)
    fieldsets = (
        (_('Details'), {
            'fields': ('title', 'description', 'price', 'attendee_type', 'event',)
        }),
        (_('Availability'), {
            'fields': ('date_from', 'date_to', 'status')
        }),
    )

admin.site.register(TicketType, TicketTypeAdmin)


admin.site.register(Receipt)
admin.site.register(DiscountCode)
admin.site.register(Ticket)
admin.site.register(Room)
admin.site.register(Schedule)
