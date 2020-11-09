from django import forms

from paikkala.models import Zone


class PrintForm(forms.Form):
    zones = forms.ModelMultipleChoiceField(queryset=Zone.objects.none(), required=False)
    included_numbers = forms.CharField(required=False)
    excluded_numbers = forms.CharField(required=False)
    exclude_reserved_seats = forms.BooleanField(initial=True, required=False)
