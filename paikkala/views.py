from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseRedirect
from django.views.generic import DeleteView, DetailView, UpdateView

from paikkala.forms import ReservationForm
from paikkala.models import Program, Ticket
from paikkala.style import compute_program_style


class MessageTemplateMixin:
    success_message_template = None

    def do_success_message(self, env):
        if self.success_message_template:
            messages.success(self.request, self.success_message_template.format_map(env))


class RelinquishView(MessageTemplateMixin, DeleteView):
    require_same_user = True
    model = Ticket
    success_url = '/'

    def get_object(self, queryset=None):
        ticket = super().get_object(queryset)
        if ticket.key != self.request.POST.get('key'):
            raise ValueError('Invalid ticket key')
        if self.require_same_user and ticket.user_id and ticket.user != self.request.user:
            raise PermissionDenied('You are not allowed to relinquish this ticket')
        return ticket

    def delete(self, request, *args, **kwargs):
        resp = super().delete(request, *args, **kwargs)
        self.do_success_message({
            'ticket': self.object,
            'program': self.object.program,
        })
        return resp


class ReservationView(MessageTemplateMixin, UpdateView):
    model = Program
    form_class = ReservationForm
    success_url = '/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        with transaction.atomic():
            tickets = form.save()
            self.do_success_message({
                'n': len(tickets),
                'program': self.object,
            })
            return HttpResponseRedirect(self.get_success_url())

    def get_object(self, queryset=None):
        program = super().get_object(queryset)
        self.precheck_reservable(program)
        return program

    def precheck_reservable(self, program):
        program.check_reservable()


class InspectionView(DetailView):
    require_same_user = True
    model = Ticket
    queryset = Ticket.objects.select_related('program', 'zone')

    def get_object(self, queryset=None):
        ticket = super().get_object(queryset)
        if ticket.key != self.kwargs.get('key'):
            raise PermissionDenied('Invalid ticket key')
        if self.require_same_user and ticket.user_id and ticket.user != self.request.user:
            raise PermissionDenied('This ticket is not yours')
        return ticket

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket = context['ticket']
        if ticket.user_id:
            # Show all of the user's tickets for the program.
            # Use case: the user has reserved a batch of adjacent seats for their friends;
            # they'll be easy to show to the security staff as they're on the same screen.
            context['tickets'] = self.queryset.filter(user=ticket.user, program=ticket.program).order_by('row', 'number')
        else:
            # If the ticket is not user-bound, only show that one.
            context['tickets'] = [ticket]
        context['program_style'] = compute_program_style(ticket.program)
        return context
