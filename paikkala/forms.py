from django import forms

from paikkala.models import Zone, Program


class ReservationForm(forms.ModelForm):
    max_count = 5

    zone = forms.ModelChoiceField(
        empty_label=None,
        queryset=Zone.objects.none(),
        widget=forms.RadioSelect(),
    )
    count = forms.IntegerField(min_value=1, initial=1)

    class Meta:
        fields = ()
        model = Program

    def __init__(self, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ReservationForm, self).__init__(**kwargs)
        self.fields['zone'].queryset = self.instance.zones.all().order_by('name')

    def save(self, commit=True):
        assert commit
        return list(
            self.instance.reserve(
                user=self.user,
                zone=self.cleaned_data['zone'],
                count=self.cleaned_data['count'],
            )
        )
