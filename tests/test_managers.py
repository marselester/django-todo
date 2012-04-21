# -*- coding: utf-8 -*-
import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from todo.models import Chain, Task


class ChainWaitTest(TestCase):
    """Тестирует случай, когда цепочка ожидает начала работы."""


class ChainWork(TestCase):
    """Тестирует случай, когда цепочка выполняется."""


class ChainDoneInTimeTest(TestCase):
    """Тестирует случай, когда цепочка выполнена вовремя."""


class ChainDoneLateTest(TestCase):
    """Тестирует случай, когда цепочка выполнена с опозданием."""


class ChainStopTest(TestCase):
    """Тестирует случай, когда цепочка остановлена."""
