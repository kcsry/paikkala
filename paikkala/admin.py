from django.contrib import admin

from paikkala.models import Program, Row, Ticket, Zone


class RowInline(admin.TabularInline):
    model = Row


class ZoneAdmin(admin.ModelAdmin):
    inlines = [RowInline]
    list_display = ('name', 'capacity')


class ProgramAdmin(admin.ModelAdmin):
    list_display = (
        'name',
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

    def reserved_tickets(self, instance):
        return instance.tickets.count()


class TicketAdmin(admin.ModelAdmin):
    list_select_related = ('program', 'zone', 'row')
    list_filter = ('program', 'zone')
    search_fields = ('user__username',)
    list_display = ('id', 'program', 'zone', 'row', 'number')
    raw_id_fields = ('user',)


admin.site.register(Program, ProgramAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Zone, ZoneAdmin)
