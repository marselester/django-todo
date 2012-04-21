# -*- coding: utf-8 -*-
import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from todo.models import Chain, Task


class ChainTest(TestCase):
    fixtures = ['test_staff.json']

    def setUp(self, chain_start_date):
        Task.objects.all().delete()
        Chain.objects.all().delete()
        # Сотрудники из test_staff.json
        manager = User.objects.get(username='alexander')
        designer = User.objects.get(username='kazimir')
        ui_engineer = User.objects.get(username='andy')
        web_app_developer = User.objects.get(username='ada')
        content_manager = User.objects.get(username='homer')
        chain = Chain.objects.create(name='Chain', owner=manager,
                                     start_date=chain_start_date)
        # First task is design for 5 days.
        deadline_design = chain_start_date + datetime.timedelta(days=5)
        Task.objects.create(worker=designer, task='Design',
                            deadline=deadline_design, chain=chain,
                            order=Task.FIRST_TASK)
        # Second task is layout for 2 days.
        deadline_layout = deadline_design + datetime.timedelta(days=2)
        Task.objects.create(worker=ui_engineer, task='Layout',
                            deadline=deadline_layout, chain=chain,
                            order=Task.FIRST_TASK + 1)
        # Third task is core for 4 days.
        deadline_core = deadline_layout + datetime.timedelta(days=4)
        Task.objects.create(worker=web_app_developer, task='Core',
                            deadline=deadline_core, chain=chain,
                            order=Task.FIRST_TASK + 2)
        # Fourth task is core for 1 day.
        deadline_content = deadline_core + datetime.timedelta(days=1)
        Task.objects.create(worker=content_manager, task='Content',
                            deadline=deadline_content, chain=chain,
                            order=Task.FIRST_TASK + 3)


class ChainWaitTest(ChainTest):
    """Тестирует случай, когда цепочка ожидает начала работы."""
    def setUp(self):
        today = datetime.date.today()
        chain_start_date = today - datetime.timedelta(days=1)
        super(ChainWaitTest, self).setUp(chain_start_date)


class ChainWork(TestCase):
    """Тестирует случай, когда цепочка выполняется."""


class ChainDoneInTimeTest(TestCase):
    """Тестирует случай, когда цепочка выполнена вовремя."""


class ChainDoneLateTest(TestCase):
    """Тестирует случай, когда цепочка выполнена с опозданием."""


class ChainStopTest(TestCase):
    """Тестирует случай, когда цепочка остановлена."""
