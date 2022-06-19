from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from paikkala.models import Row, SeatQualifier


class RowInline(admin.TabularInline):
    model = Row
    readonly_fields = ('capacity',)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related('zone', 'zone__room')


class SeatQualifierInline(admin.TabularInline):
    model = SeatQualifier

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).select_related('zone')


class ZoneAdmin(admin.ModelAdmin):
    inlines = [RowInline, SeatQualifierInline]
    list_select_related = ('room',)
    list_display = ('name', 'room', 'capacity')
    list_filter = ('room',)
