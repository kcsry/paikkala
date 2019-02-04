from django.contrib import admin

from paikkala.models import Program, Row, Ticket, Zone, Room
from paikkala.models.blocks import PerProgramBlock


class OptimizedRowQueryMixin:

    def get_field_queryset(self, db, db_field, request):
        queryset = super().get_field_queryset(db, db_field, request)
        if db_field.name in ('row', 'rows'):
            queryset = (queryset or Row.objects.all()).select_related('zone', 'zone__room')
        return queryset


class RowInline(admin.TabularInline):
    model = Row
    readonly_fields = ('capacity',)


class ZoneAdmin(admin.ModelAdmin):
    inlines = [RowInline]
    list_select_related = ('room',)
    list_display = ('name', 'room', 'capacity')
    list_filter = ('room',)


class RoomAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name',)


class PerProgramBlockInline(OptimizedRowQueryMixin, admin.TabularInline):
    model = PerProgramBlock


class ProgramAdmin(OptimizedRowQueryMixin, admin.ModelAdmin):
    list_display = (
        'name',
        'event_name',
        'room',
        'reservation_start',
        'reservation_end',
        'reserved_tickets',
        'max_tickets',
        'require_user',
        'max_tickets_per_user',
        'max_tickets_per_batch',
    )
    filter_horizontal = (
        'rows',
    )
    list_filter = (
        'event_name',
        'room',
    )
    list_select_related = (
        'room',
    )
    search_fields = (
        'name',
    )
    inlines = [
        PerProgramBlockInline,
    ]

    def reserved_tickets(self, instance):
        return instance.tickets.count()

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Deferred calculation of max tickets when creating a new Program
        if not change and form.instance.automatic_max_tickets:
            form.instance.clean()
            form.instance.save(update_fields=('max_tickets',))


class TicketAdmin(admin.ModelAdmin):
    list_select_related = ('program', 'zone', 'row')
    list_filter = ('program', 'zone')
    search_fields = ('user__username',)
    list_display = ('id', 'program', 'zone', 'row', 'number')
    raw_id_fields = ('user',)


admin.site.register(Program, ProgramAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Zone, ZoneAdmin)
admin.site.register(Room, RoomAdmin)
