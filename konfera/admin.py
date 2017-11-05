from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from konfera.forms import OrderedTicketsInlineFormSet
from konfera.models import Receipt, Order, Event, TicketType, DiscountCode, Ticket, Speaker, Talk, Organizer


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_from', 'date_to', 'cfp_end', 'status')
    list_filter = ('status',)
    ordering = ('date_from', 'date_to', 'title')
    search_fields = ('=title',)
    readonly_fields = ('uuid', 'date_created', 'date_modified')
    fieldsets = (
        (_('Description'), {
            'fields': ('title', 'slug', 'organizer',),
        }),
        (_('Dates'), {
            'fields': ('date_from', 'date_to', 'cfp_end'),
        }),
        (_('Details'), {
            'fields': ('uuid', 'status',),
        }),
        (_('Modifications'), {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',),
        }),
    )
    prepopulated_fields = {
        'slug': ('title',),
    }


admin.site.register(Event, EventAdmin)


class SpeakerTalksInline(admin.StackedInline):
    model = Talk
    verbose_name = _("Speaker's talk")
    verbose_name_plural = _("Speaker's talks")
    fk_name = "primary_speaker"
    extra = 0


class SecondarySpeakerTalksInline(admin.StackedInline):
    model = Talk
    verbose_name = _("Secondary speaker's talk")
    verbose_name_plural = _("Secondary speaker's talks")
    fk_name = "secondary_speaker"
    extra = 0


class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'country', 'social_url',)
    list_filter = ('country', 'title')
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
            'fields': ('bio', 'country', ('url', 'social_url',), 'image',)
        }),
        (_('Modifications'), {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',),
        }),
    )
    inlines = [
        SpeakerTalksInline,
        SecondarySpeakerTalksInline,
    ]


admin.site.register(Speaker, SpeakerAdmin)


class TalkAdmin(admin.ModelAdmin):
    list_display = ('title', 'speaker', 'flag', 'type', 'duration', 'event', 'status',)
    list_filter = ('type', 'duration', 'status', 'event', 'flag')
    search_fields = ('=title', '=primary_speaker__first_name', '=primary_speaker__last_name', '=event__title')
    ordering = ('title', 'event')
    readonly_fields = ('date_created', 'date_modified', 'uuid')
    fieldsets = (
        (_('Description'), {
            'fields': ('title', 'abstract', 'flag',  'language', 'event',)
        }),
        (_('Details'), {
            'fields': (('type', 'duration',), 'status', ('primary_speaker', 'secondary_speaker',), 'uuid',)
        }),
        (_('Modifications'), {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',),
        }),
    )
    actions = ['make_draft', 'make_approved', 'make_published', 'make_rejected', 'make_withdrawn']

    def make_draft(self, request, queryset):
        rows_updated = queryset.update(status=Talk.DRAFT)
        self.message_user(request, "%s talk(s) status updated." % rows_updated)

    def make_approved(self, request, queryset):
        rows_updated = queryset.update(status=Talk.APPROVED)
        self.message_user(request, "%s talk(s) status updated." % rows_updated)

    def make_published(self, request, queryset):
        rows_updated = queryset.update(status=Talk.PUBLISHED)
        self.message_user(request, "%s talk(s) status updated." % rows_updated)

    def make_rejected(self, request, queryset):
        rows_updated = queryset.update(status=Talk.REJECTED)
        self.message_user(request, "%s talk(s) status updated." % rows_updated)

    def make_withdrawn(self, request, queryset):
        rows_updated = queryset.update(status=Talk.WITHDRAWN)
        self.message_user(request, "%s talk(s) status updated." % rows_updated)

    make_draft.short_description = "Set selected talks to draft"
    make_approved.short_description = "Set selected talks to approved"
    make_published.short_description = "Set selected talks to published"
    make_rejected.short_description = "Set selected talks to rejected"
    make_withdrawn.short_description = "Set selected talks to withdrawn"

    def speaker(self, obj):
        info = (Speaker._meta.app_label, Speaker._meta.model_name)
        link = reverse("admin:%s_%s_change" % info, args=(obj.primary_speaker.id,))
        return mark_safe('<a href="%s">%s</a>' % (link, obj.primary_speaker))


admin.site.register(Talk, TalkAdmin)


class OrderedTicketsInline(admin.TabularInline):
    model = Ticket
    verbose_name = _('Ordered ticket')
    verbose_name_plural = _('Ordered tickets')
    extra = 1
    formset = OrderedTicketsInlineFormSet


class ReceiptInline(admin.StackedInline):
    model = Receipt


class OrderAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'variable_symbol', 'purchase_date', 'price', 'discount', 'processing_fee', 'to_pay',
                    'status', 'receipt_of')
    list_filter = ('status', 'purchase_date')
    ordering = ('-purchase_date',)
    readonly_fields = [
        'purchase_date', 'uuid', 'date_created', 'date_modified', 'variable_symbol', 'price', 'discount', 'to_pay',
        'unpaid_notification_sent_at',
    ]
    fieldsets = (
        (_('Details'), {
            'fields': ('uuid', 'variable_symbol', 'price', 'discount', 'processing_fee', 'to_pay', 'status',
                       'amount_paid', 'unpaid_notification_sent_at'),
        }),
        (_('Modifications'), {
            'fields': ('purchase_date', 'payment_date', 'date_created', 'date_modified'),
            'classes': ('collapse',),
        }),
    )
    inlines = [
        ReceiptInline, OrderedTicketsInline
    ]
    actions = ['make_paid']

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status not in (Order.AWAITING, Order.PARTLY_PAID):
            return self.readonly_fields + ['amount_paid', 'payment_date', 'processing_fee']

        return self.readonly_fields

    def make_paid(self, request, queryset):
        rows_updated = queryset.update(status=Order.PAID)
        self.message_user(request, "%s order(s) status updated." % rows_updated)

    make_paid.short_description = "Mark selected order as paid"


admin.site.register(Order, OrderAdmin)


class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'attendee_type', 'event', 'available_tickets', 'status', 'accessibility')
    list_filter = ('attendee_type', 'accessibility', 'event')
    search_fields = ('=title',)
    ordering = ('event', 'title', 'date_from')
    readonly_fields = ('status', 'uuid', 'date_created', 'date_modified', 'issued_tickets', 'available_tickets')
    fieldsets = (
        (_('Details'), {
            'fields': ('title', 'description', 'uuid', 'price', 'attendee_type', 'event',)
        }),
        (_('Availability'), {
            'fields': ('date_from', 'date_to', 'status', 'accessibility', 'usage', 'issued_tickets',
                       'available_tickets'),
            'classes': ('collapse',),
        }),
        (_('Modifications'), {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',),
        }),
    )
    actions = ['make_public']

    def make_public(self, request, queryset):
        rows_updated = queryset.update(accessibility=TicketType.PUBLIC)
        if rows_updated == 1:
            message_bit = "1 Ticket type was"
        else:
            message_bit = "%s Ticket types were" % rows_updated
        self.message_user(request, "%s successfully marked as public." % message_bit)

    make_public.short_description = "Mark selected Ticket types as public"


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
            'fields': ('discount', 'usage')
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
    list_display = ('email', 'first_name', 'last_name', 'type', 'status', 'link_to_order')
    list_filter = ('status', 'order__status', 'type__attendee_type', 'type__event')
    ordering = ('-order__purchase_date', 'email')
    search_fields = ('=last_name', '=first_name', '=email')  # case insensitive searching
    readonly_fields = ('uuid', 'link_to_order', 'date_created', 'date_modified')
    fieldsets = (
        (_('Personal details'), {
            'fields': ('title', 'first_name', 'last_name', 'email', 'phone')
        }),
        (_('Ticket info'), {
            'fields': ('uuid', 'link_to_order', 'type', 'discount_code', 'status', 'description')
        }),
        (_('Modifications'), {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',),
        }),
    )
    actions = ['make_checked_in']

    def make_checked_in(self, request, queryset):
        rows_updated = queryset.update(status=Ticket.CHECKEDIN)
        self.message_user(request, "%s visitor(s) checked in." % rows_updated)

    make_checked_in.short_description = "Mark selected Tickets as checked in"

    def link_to_order(self, obj):
        info = (Order._meta.app_label, Order._meta.model_name)
        link = reverse("admin:%s_%s_change" % info, args=(obj.order.id,))
        return mark_safe('<a href="%s">%s</a>' % (link, obj.order.uuid))

    link_to_order.short_description = "Order"


admin.site.register(Ticket, TicketAdmin)


class OrganizerAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'country',)
    list_filter = ('organized_events',)
    ordering = ('title',)
    search_fields = ('=title',)
    readonly_fields = ('date_created', 'date_modified',)
    fieldsets = (
        (_('Basic Info'), {
            'fields': ('title',),
        }),
        (_('Address'), {
            'fields': ('street', 'street2', 'city', 'postcode', 'state', 'country',),
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
