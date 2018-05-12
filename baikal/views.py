from django.views.generic import ListView

from paikkala.models import Program, Ticket
from paikkala.views import ReservationView as BaseReservationView


class ReservationView(BaseReservationView):
    template_name = 'reserve.html'


class IndexView(ListView):
    template_name = 'index.html'
    queryset = Ticket.objects.select_related('program', 'zone', 'row')
    context_object_name = 'tickets'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['programs'] = Program.objects.all()
        return context
