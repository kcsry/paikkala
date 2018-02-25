from django.db import transaction
from django.views.generic import ListView, UpdateView

from paikkala.forms import ReservationForm
from paikkala.models import Program, Ticket


class ReservationView(UpdateView):
    model = Program
    form_class = ReservationForm
    template_name = 'reserve.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return '/'

    def form_valid(self, form):
        with transaction.atomic():
            return super().form_valid(form)


class IndexView(ListView):
    template_name = 'index.html'
    queryset = Ticket.objects.select_related('program', 'zone', 'row')
    context_object_name = 'tickets'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['programs'] = Program.objects.all()
        return context
