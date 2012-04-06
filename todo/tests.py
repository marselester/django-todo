# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth.models import User

from todo.models import Chain, Task


class ActualStatusTest(TestCase):
    def setUp(self):
        Task.objects.all().delete()
        Chain.objects.all().delete()
        User.objects.all().delete()
        self.manager = User.objects.create_user('manager', 'manager@test.com')
        self.designer = User.objects.create_user('designer',
                                                 'designer@test.com')
        self.programmer = User.objects.create_user('programmer',
                                                   'programmer@test.com')

    def testFirstTaskWait(self):
        """Тестирует статус WAIT у первой задачи.

        Задача стоит первой в цепочке и дата начала работы над цепочкой еще
        не наступила.
        """
        now = datetime.now()
        chain_start_date = now + timedelta(days=1)
        chain = Chain.objects.create(name='Chain', start_date=chain_start_date,
                                     owner=self.manager)
        deadline = chain_start_date + timedelta(days=3)
        first_task = Task.objects.create(worker=self.designer, task='Design',
                                         deadline=deadline, chain=chain,
                                         order=Task.FIRST_TASK)
        self.assertEqual(first_task.actual_status(), Task.WAIT_STATUS)

    def testPrevTaskNotDone(self):
        """Тестирует статус WAIT, проверяя статус предыдущей задачи.

        Статус предыдущей задачи не должен быть DONE.
        """
        now = datetime.now()
        chain_start_date = now - timedelta(days=1)
        chain = Chain.objects.create(name='Chain', start_date=chain_start_date,
                                     owner=self.manager)
        deadline_first_task = chain_start_date + timedelta(days=3)
        first_task = Task.objects.create(worker=self.designer, task='Design',
                                         deadline=deadline_first_task,
                                         chain=chain,
                                         order=Task.FIRST_TASK)
        deadline_second_task = deadline_first_task + timedelta(days=2)
        second_task = Task.objects.create(worker=self.programmer,
                                          task='Programming',
                                          deadline=deadline_second_task,
                                          chain=chain,
                                          order=Task.FIRST_TASK + 1)
        self.assertEqual(second_task.actual_status(), Task.WAIT_STATUS)

    def testFirstTaskWork(self):
        """Тестирует статус WORK у первой задачи.

        Задача стоит первой в цепочке и наступила дата начала работы над
        цепочкой.
        """
        now = datetime.now()
        chain_start_date = now - timedelta(days=1)
        chain = Chain.objects.create(name='Chain', start_date=chain_start_date,
                                     owner=self.manager)
        deadline = chain_start_date + timedelta(days=3)
        first_task = Task.objects.create(worker=self.designer, task='Design',
                                         deadline=deadline, chain=chain,
                                         order=Task.FIRST_TASK)
        self.assertEqual(first_task.actual_status(), Task.WORK_STATUS)

    def testPrevTaskDone(self):
        """Тестирует статус WORK, проверяя статус предыдущей задачи.

        Статус предыдущей задачи должен быть DONE. Цепочка начала работать 2
        дня назад, на дизайн выделено 3 дня, задача была выполнена за 2 дня.
        Программист досрочно (на 1 день раньше) получил результаты работы
        дизайнера.
        """
        now = datetime.now()
        chain_start_date = now - timedelta(days=2)
        chain = Chain.objects.create(name='Chain', start_date=chain_start_date,
                                     owner=self.manager)
        deadline_first_task = chain_start_date + timedelta(days=3)
        first_task = Task.objects.create(worker=self.designer, task='Design',
                                         deadline=deadline_first_task,
                                         finish_date=now,
                                         chain=chain,
                                         order=Task.FIRST_TASK,
                                         status=Task.DONE_STATUS)
        deadline_second_task = deadline_first_task + timedelta(days=2)
        second_task = Task.objects.create(worker=self.programmer,
                                          task='Programming',
                                          deadline=deadline_second_task,
                                          chain=chain,
                                          order=Task.FIRST_TASK + 1)
        self.assertEqual(second_task.actual_status(), Task.WORK_STATUS)
