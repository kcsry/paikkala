from django.contrib import admin
from paikkala.models import Row


class RowInline(admin.TabularInline):
    model = Row
    readonly_fields = ('capacity',)


class ZoneAdmin(admin.ModelAdmin):
    inlines = [RowInline]
    list_select_related = ('room',)
    list_display = ('name', 'room', 'capacity')
    list_filter = ('room',)
