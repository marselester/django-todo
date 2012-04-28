# -*- coding: utf-8 -*-
import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from todo.models import Chain, Task
from . import factories


class ChainTest(TestCase):
    def setUp(self):
        factories.make_fixtures()


class ChainWaitTest(ChainTest):
    """Тестирует случай, когда цепочка ожидает начала работы."""


class ChainWorkTest(ChainTest):
    """Тестирует случай, когда цепочка выполняется."""


class ChainDoneInTimeTest(ChainTest):
    """Тестирует случай, когда цепочка выполнена вовремя."""


class ChainDoneLateTest(ChainTest):
    """Тестирует случай, когда цепочка выполнена с опозданием."""


class ChainStopTest(ChainTest):
    """Тестирует случай, когда цепочка остановлена."""
