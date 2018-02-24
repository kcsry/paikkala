from django.contrib import admin

from paikkala.models import Program, Ticket, Zone, Row


class RowInline(admin.TabularInline):
    model = Row


class ZoneAdmin(admin.ModelAdmin):
    inlines = [RowInline]


admin.site.register(Program)
admin.site.register(Ticket)
admin.site.register(Zone, ZoneAdmin)
