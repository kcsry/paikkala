from django.contrib import admin


class RoomAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name',)
