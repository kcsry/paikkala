import os
from collections.abc import Iterator
from contextlib import contextmanager

import monkeytype


class Config(monkeytype.config.DefaultConfig):

    @contextmanager
    def cli_context(self, command: str) -> Iterator[None]:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baikal.settings')
        import django
        django.setup()
        yield


CONFIG = Config()
