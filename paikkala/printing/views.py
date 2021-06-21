from django.forms import CheckboxSelectMultiple
from django.http import HttpResponse
from django.views.generic import DetailView, FormView

from paikkala.models import Program
from paikkala.printing import generate_ticket_pdf
from paikkala.printing.configuration import PrintingConfiguration
from paikkala.printing.drawing import TicketDrawer
from paikkala.printing.forms import PrintForm
from paikkala.utils.ranges import parse_number_set


class PrintView(FormView, DetailView):
    model = Program
    context_object_name = "program"
    form_class = PrintForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["zones"].widget = CheckboxSelectMultiple()
        form.fields["zones"].queryset = self.object.zones.all()
        form.fields["exclude_reserved_seats"].help_text = (
            "%d currently reserved" % self.object.tickets.count()
        )
        return form

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        included_numbers = parse_number_set(form.cleaned_data["included_numbers"])
        excluded_numbers = parse_number_set(form.cleaned_data["excluded_numbers"])
        if form.cleaned_data["exclude_reserved_seats"]:
            excluded_numbers |= set(
                self.object.tickets.values_list("number", flat=True)
            )
        pdf_bytes = generate_ticket_pdf(
            drawer_class=self.get_drawer_class(),
            configuration=self.get_ticket_configuration(),
            program=self.object,
            zones=form.cleaned_data["zones"],
            included_numbers=included_numbers,
            excluded_numbers=excluded_numbers,
        )
        return HttpResponse(content=pdf_bytes, content_type="application/pdf",)

    def get_ticket_configuration(self):
        return PrintingConfiguration()

    def get_drawer_class(self):
        return TicketDrawer
