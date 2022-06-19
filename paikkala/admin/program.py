from django.contrib import admin

from paikkala.models import PerProgramBlock, Program, Row


class OptimizedRowQueryMixin:
    def get_field_queryset(self, db, db_field, request):  # noqa: ANN001,ANN201
        queryset = super().get_field_queryset(db, db_field, request)
        if db_field.name in ('row', 'rows'):
            queryset = (queryset or Row.objects.all()).select_related('zone', 'zone__room')
        return queryset  # noqa: R504


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

    def reserved_tickets(self, instance: Program) -> int:
        return instance.tickets.count()

    def save_related(self, request, form, formsets, change):  # noqa: ANN001,ANN201
        super().save_related(request, form, formsets, change)
        # Deferred calculation of max tickets when creating a new Program
        if not change and form.instance.automatic_max_tickets:
            form.instance.clean()
            form.instance.save(update_fields=('max_tickets',))
