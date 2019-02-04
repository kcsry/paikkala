import pytest
from django.core.management import call_command

from paikkala.models import Program


@pytest.mark.django_db
def test_demo_data():
    assert not Program.objects.exists()
    call_command('paikkala_load_demo_data', yes=True)
    prog = Program.objects.get()
    assert prog.tickets.exists()
