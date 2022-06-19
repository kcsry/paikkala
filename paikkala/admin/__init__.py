from django.contrib import admin

from paikkala.admin.program import ProgramAdmin
from paikkala.admin.room import RoomAdmin
from paikkala.admin.ticket import TicketAdmin
from paikkala.admin.zone import ZoneAdmin
from paikkala.models import Program, Room, Ticket, Zone

admin.site.register(Program, ProgramAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Zone, ZoneAdmin)
admin.site.register(Room, RoomAdmin)
