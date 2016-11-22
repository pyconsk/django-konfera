from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from konfera.forms import OrderedTicketsInlineFormSet
from konfera.models import (Receipt, Order, Location, Event, Sponsor, TicketType, DiscountCode, Ticket, Speaker, Talk,
                            Room, Schedule, Organizer)


class SponsorshipInline(admin.TabularInline):
    model = Event.sponsors.through
    extra = 1


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_from', 'date_to', 'cfp_end', 'event_type', 'status')
    list_filter = ('event_type', 'status')
    ordering = ('date_from', 'date_to', 'title')
    search_fields = ('=title',)
    readonly_fields = ('uuid', 'date_created', 'date_modified')
    fieldsets = (
        (_('Description'), {
            'fields': ('title', 'slug', 'organizer', 'description', 'contact_email'),
        }),
        (_('Dates'), {
            'fields': ('date_from', 'date_to', 'cfp_end'),
        }),
        (_('Details'), {
            'fields': ('uuid', 'event_type', 'status', 'location', 'cfp_allowed', 'footer_text', 'analytics'),
        }),
        (_('Code of Conduct'), {
            'fields': ('coc', 'coc_phone', 'coc_phone2'),
        }),
        (_('Modifications'), {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',),
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
    readonly_fields = ('date_created', 'date_modified')
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
        (_('Modifications'), {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',),
        }),
    )


admin.site.register(Speaker, SpeakerAdmin)


class TalkAdmin(admin.ModelAdmin):
    list_display = ('title', 'primary_speaker', 'type', 'duration', 'event', 'status',)
    list_filter = ('type', 'duration', 'event', 'status',)
    search_fields = ('=title', '=primary_speaker__first_name', '=primary_speaker__last_name', '=event__title')
    ordering = ('title', 'event')
    readonly_fields = ('date_created', 'date_modified', 'uuid')
    fieldsets = (
        (_('Description'), {
            'fields': ('title', 'abstract', 'event',)
        }),
        (_('Details'), {
            'fields': (('type', 'duration',), 'status', ('primary_speaker', 'secondary_speaker',), 'uuid',)
        }),
        (_('Modifications'), {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',),
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
    readonly_fields = ('date_created', 'date_modified')
    fieldsets = (
        (_('Details'), {
            'fields': ('title', 'type', 'logo', 'url', 'about_us',)
        }),
        (_('Modifications'), {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',),
        }),
    )
    inlines = [
        SponsoredEventsInline,
        SponsoredSpeakersInline,
    ]


admin.site.register(Sponsor, SponsorAdmin)


class RoomsInline(admin.StackedInline):
    model = Room
    extra = 1


class LocationAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'capacity')
    list_filter = ('city',)
    ordering = ('city', 'title')
    readonly_fields = ('date_created', 'date_modified')
    fieldsets = (
        (_('Details'), {
            'fields': ('title', 'website', 'capacity',)
        }),
        (_('Address'), {
            'fields': ('street', 'street2', 'state', 'city', 'postcode', 'get_here')
        }),
        (_('Modifications'), {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',),
        }),
    )
    inlines = [
        RoomsInline,
    ]


admin.site.register(Location, LocationAdmin)


class OrderedTicketsInline(admin.StackedInline):
    model = Ticket
    verbose_name = _('Ordered ticket')
    verbose_name_plural = _('Ordered tickets')
    extra = 1
    formset = OrderedTicketsInlineFormSet


class ReceiptInline(admin.StackedInline):
    model = Receipt


class OrderAdmin(admin.ModelAdmin):
    list_display = ('purchase_date', 'price', 'discount', 'status', 'receipt_of')
    list_filter = ('status',)
    ordering = ('purchase_date',)
    search_fields = ('=uuid',)
    readonly_fields = (
        'purchase_date', 'payment_date', 'amount_paid', 'uuid', 'date_created', 'date_modified', 'variable_symbol',
        'price', 'discount', 'to_pay',
    )
    fieldsets = (
        (_('Details'), {
            'fields': ('uuid', 'variable_symbol', 'price', 'discount', 'to_pay', 'status', 'amount_paid'),
        }),
        (_('Modifications'), {
            'fields': ('purchase_date', 'payment_date', 'date_created', 'date_modified'),
            'classes': ('collapse',),
        }),
    )
    inlines = [
        ReceiptInline, OrderedTicketsInline
    ]


admin.site.register(Order, OrderAdmin)


class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'attendee_type', 'event', 'status', 'accessibility')
    list_filter = ('attendee_type', 'accessibility')
    ordering = ('event', 'title', 'date_from')
    readonly_fields = ('status', 'uuid', 'date_created', 'date_modified')
    fieldsets = (
        (_('Details'), {
            'fields': ('title', 'description', 'uuid', 'price', 'attendee_type', 'event',)
        }),
        (_('Availability'), {
            'fields': ('date_from', 'date_to', 'status', 'accessibility'),
            'classes': ('collapse',),
        }),
        (_('Modifications'), {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',),
        }),
    )


admin.site.register(TicketType, TicketTypeAdmin)


class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount', 'ticket_type', 'usage', 'issued_tickets')
    ordering = ('title', 'ticket_type')
    readonly_fields = ('date_created', 'date_modified')
    fieldsets = (
        (_('Details'), {
            'fields': ('title', 'hash', 'ticket_type')
        }),
        (_('Discount'), {
            'fields': ('discount', 'usage', 'issued_tickets')
        }),
        (_('Availability'), {
            'fields': ('date_from', 'date_to'),
            'classes': ('collapse',),
        }),
        (_('Modifications'), {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',),
        }),
    )


admin.site.register(DiscountCode, DiscountCodeAdmin)


class TicketAdmin(admin.ModelAdmin):
    list_display = ('email', 'type', 'status')
    list_filter = ('status', 'type__event',)
    ordering = ('order__purchase_date', 'email')
    search_fields = ('=last_name', '=first_name', '=email',)  # case insensitive searching
    readonly_fields = ('order', 'date_created', 'date_modified')
    fieldsets = (
        (_('Personal details'), {
            'fields': ('title', 'first_name', 'last_name', 'email', 'phone')
        }),
        (_('Ticket info'), {
            'fields': ('order', 'type', 'discount_code', 'status', 'description')
        }),
        (_('Modifications'), {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',),
        }),
    )


admin.site.register(Ticket, TicketAdmin)


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('start', 'duration', 'talk', 'room')
    list_filter = ('talk__event', 'room')
    ordering = ('start', 'room', 'event')
    search_fields = ('=description',)
    readonly_fields = ('date_created', 'date_modified')
    fieldsets = (
        (_('Time'), {
            'fields': ('start', 'duration'),
        }),
        (_('Details'), {
            'fields': ('event', 'talk', 'room', 'description')
        }),
        (_('Modifications'), {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',),
        }),
    )


admin.site.register(Schedule, ScheduleAdmin)


class OrganizerAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'country',)
    list_filter = ('organized_events',)
    ordering = ('title',)
    search_fields = ('=title',)
    readonly_fields = ('date_created', 'date_modified',)
    fieldsets = (
        (_('Basic Info'), {
            'fields': ('title', 'about_us'),
        }),
        (_('Address'), {
            'fields': ('street', 'street2', 'city', 'country',),
        }),
        (_('Legal details'), {
            'fields': ('company_id', 'tax_id', 'vat_id',),
            'classes': ('collapse',),
        }),
        (_('Modifications'), {
            'fields': ('date_created', 'date_modified',),
            'classes': ('collapse',),
        }),
    )


admin.site.register(Organizer, OrganizerAdmin)
