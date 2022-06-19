from django.contrib import admin


class TicketAdmin(admin.ModelAdmin):
    list_select_related = ('program', 'zone', 'row')
    list_filter = ('program', 'zone')
    search_fields = ('user__username',)
    list_display = ('id', 'program', 'zone', 'row', 'number')
    raw_id_fields = ('user',)
