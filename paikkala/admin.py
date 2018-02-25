from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple

from paikkala.models import Program, Ticket, Zone, Row


class RowInline(admin.TabularInline):
    model = Row


class ZoneAdmin(admin.ModelAdmin):
    inlines = [RowInline]
    list_display = ('name', 'capacity')


class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'reservation_start', 'reservation_end', 'reserved_tickets', 'max_tickets')
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

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
