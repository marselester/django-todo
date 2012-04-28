# -*- coding: utf-8 -*-
import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from todo.models import Chain, Task
from . import factories


class TaskTest(TestCase):
    def setUp(self):
        factories.make_fixtures()
        # Сотрудники.
        self.manager = User.objects.get(username='alexander')
        self.designer = User.objects.get(username='kazimir')
        self.programmer = User.objects.get(username='ada')


class ActualStatusTest(TaskTest):
    """Тестирует определение статуса задачи."""
    def test_first_task_wait(self):
        """Тестирует статус WAIT у первой задачи.

        Задача стоит первой в цепочке и дата начала работы над цепочкой еще
        не наступила. Цепочка начнет работать через 1 день, на дизайн выделено
        3 дня.
        """
        today = datetime.date.today()
        chain_start_date = today + datetime.timedelta(days=1)
        chain = Chain.objects.create(name='Chain', start_date=chain_start_date,
                                     owner=self.manager)
        deadline = chain_start_date + datetime.timedelta(days=3)
        first_task = Task.objects.create(worker=self.designer, task='Design',
                                         deadline=deadline, chain=chain,
                                         order=Task.FIRST_TASK)
        self.assertEqual(first_task.actual_status(), Task.WAIT_STATUS)

    def test_prev_task_not_done(self):
        """Тестирует статус WAIT, проверяя статус предыдущей задачи.

        Статус предыдущей задачи не должен быть DONE. Цепочка начала работать 1
        день назад, на дизайн выделено 3 дня, задача выполняется второй день.
        Программист ожидает результы работы дизайнера через 1 день
        (послезавтра).
        """
        today = datetime.date.today()
        chain_start_date = today - datetime.timedelta(days=1)
        chain = Chain.objects.create(name='Chain', start_date=chain_start_date,
                                     owner=self.manager)
        deadline_first_task = chain_start_date + datetime.timedelta(days=3)
        Task.objects.create(worker=self.designer, task='Design', chain=chain,
                            deadline=deadline_first_task,
                            order=Task.FIRST_TASK)
        deadline_second_task = deadline_first_task + datetime.timedelta(days=2)
        second_task = Task.objects.create(worker=self.programmer,
                                          task='Programming',
                                          deadline=deadline_second_task,
                                          chain=chain,
                                          order=Task.FIRST_TASK + 1)
        self.assertEqual(second_task.actual_status(), Task.WAIT_STATUS)

    def test_first_task_work(self):
        """Тестирует статус WORK у первой задачи.

        Задача стоит первой в цепочке и наступила дата начала работы над
        цепочкой. Цепочка начала работать 1 день назад, на дизайн выделено
        3 дня.
        """
        today = datetime.date.today()
        chain_start_date = today - datetime.timedelta(days=1)
        chain = Chain.objects.create(name='Chain', start_date=chain_start_date,
                                     owner=self.manager)
        deadline = chain_start_date + datetime.timedelta(days=3)
        first_task = Task.objects.create(worker=self.designer, task='Design',
                                         deadline=deadline, chain=chain,
                                         order=Task.FIRST_TASK)
        self.assertEqual(first_task.actual_status(), Task.WORK_STATUS)

    def test_prev_task_done(self):
        """Тестирует статус WORK, проверяя статус предыдущей задачи.

        Статус предыдущей задачи должен быть DONE. Цепочка начала работать 2
        дня назад, на дизайн выделено 3 дня, задача была выполнена за 2 дня.
        Программист досрочно (на 1 день раньше) получил результаты работы
        дизайнера.
        """
        today = datetime.date.today()
        chain_start_date = today - datetime.timedelta(days=2)
        chain = Chain.objects.create(name='Chain', start_date=chain_start_date,
                                     owner=self.manager)
        deadline_first_task = chain_start_date + datetime.timedelta(days=3)
        Task.objects.create(worker=self.designer, task='Design', chain=chain,
                            deadline=deadline_first_task, finish_date=today,
                            order=Task.FIRST_TASK, status=Task.DONE_STATUS)
        deadline_second_task = deadline_first_task + datetime.timedelta(days=2)
        second_task = Task.objects.create(worker=self.programmer,
                                          task='Programming',
                                          deadline=deadline_second_task,
                                          chain=chain,
                                          order=Task.FIRST_TASK + 1)
        self.assertEqual(second_task.actual_status(), Task.WORK_STATUS)


class StartDateTest(TaskTest):
    """Тестирует определение даты начала работы над задачей."""
    def test_first_task(self):
        """Тестирует дату начала работы первой задачи.

        Дата начала первой задачи совпадает с датой начала цепочки. Это условие
        верно для задач с любым статусом.
        """
        today = datetime.date.today()
        chain_start_date = today + datetime.timedelta(days=1)
        chain = Chain.objects.create(name='Chain', start_date=chain_start_date,
                                     owner=self.manager)
        deadline = chain_start_date + datetime.timedelta(days=3)
        first_task = Task.objects.create(worker=self.designer, task='Design',
                                         deadline=deadline, chain=chain,
                                         order=Task.FIRST_TASK)
        self.assertEqual(first_task.start_date(), chain.start_date)

    def test_wait(self):
        """Тестирует дату начала работы задачи со статусом WAIT.

        Дата начала совпадает с датой дедлайна предыдущей задачи (дедлайн
        не просрочен). Предыдущая задача может иметь статус WAIT, WORK, STOP.
        """
        today = datetime.date.today()
        chain_start_date = today - datetime.timedelta(days=1)
        chain = Chain.objects.create(name='Chain', start_date=chain_start_date,
                                     owner=self.manager)
        deadline_first_task = chain_start_date + datetime.timedelta(days=3)
        Task.objects.create(worker=self.designer, task='Design', chain=chain,
                            deadline=deadline_first_task,
                            order=Task.FIRST_TASK)
        deadline_second_task = deadline_first_task + datetime.timedelta(days=2)
        Task.objects.create(worker=self.programmer, task='Programming',
                            deadline=deadline_second_task, chain=chain,
                            order=Task.FIRST_TASK + 1)
        first_task = Task.objects.get(task='Design')
        second_task = Task.objects.get(task='Programming')
        self.assertEqual(second_task.start_date(), first_task.deadline)

    def test_work(self):
        """Тестирует дату начала работы задачи со статусом WORK.

        Дата начала совпадает с датой окончания предыдущей задачи (DONE). Это
        условие верно и для задач со статусом DONE или STOP.
        """
        today = datetime.date.today()
        chain_start_date = today - datetime.timedelta(days=2)
        chain = Chain.objects.create(name='Chain', start_date=chain_start_date,
                                     owner=self.manager)
        deadline_first_task = chain_start_date + datetime.timedelta(days=3)
        Task.objects.create(worker=self.designer, task='Design', chain=chain,
                            deadline=deadline_first_task, finish_date=today,
                            order=Task.FIRST_TASK, status=Task.DONE_STATUS)
        deadline_second_task = deadline_first_task + datetime.timedelta(days=2)
        Task.objects.create(worker=self.programmer, task='Programming',
                            deadline=deadline_second_task, chain=chain,
                            order=Task.FIRST_TASK + 1)
        first_task = Task.objects.get(task='Design')
        second_task = Task.objects.get(task='Programming')
        self.assertEqual(second_task.start_date(), first_task.finish_date)

    def test_unpredictable(self):
        """Тестирует непрогнозируемую дату начала работы задачи.

        Статус задачи WAIT, предыдущая задача превысила дедлайн. Предыдущая
        задача может иметь статус WAIT, WORK, STOP.
        """
        today = datetime.date.today()
        chain_start_date = today - datetime.timedelta(days=10)
        chain = Chain.objects.create(name='Chain', start_date=chain_start_date,
                                     owner=self.manager)
        deadline_first_task = chain_start_date + datetime.timedelta(days=3)
        Task.objects.create(worker=self.designer, task='Design', chain=chain,
                            deadline=deadline_first_task,
                            order=Task.FIRST_TASK)
        deadline_second_task = deadline_first_task + datetime.timedelta(days=2)
        Task.objects.create(worker=self.programmer, task='Programming',
                            deadline=deadline_second_task, chain=chain,
                            order=Task.FIRST_TASK + 1)
        second_task = Task.objects.get(task='Programming')
        self.assertEqual(second_task.start_date(), None)


class DeadlineDaysTest(TaskTest):
    """Тестирует определение количества дней до дедлайна и после него."""
    def test_before_deadline(self):
        """Тестирует случай, когда дедлайн еще не наступил.

        Задача работает второй день, на выполнение отведено 3 дня.
        """
        today = datetime.date.today()
        chain_start_date = today - datetime.timedelta(days=1)
        chain = Chain.objects.create(name='Chain', start_date=chain_start_date,
                                     owner=self.manager)
        deadline = chain_start_date + datetime.timedelta(days=3)
        first_task = Task.objects.create(worker=self.designer, task='Design',
                                         deadline=deadline, chain=chain,
                                         order=Task.FIRST_TASK)
        self.assertEqual(first_task.remaining_days(), 1)
        self.assertEqual(first_task.days_quantity_after_deadline(), None)

    def test_after_deadline(self):
        """Тестирует случай, когда дедлайн просрочен.

        Задача работает 5 день, на выполнение отведено 3 дня.
        """
        today = datetime.date.today()
        chain_start_date = today - datetime.timedelta(days=4)
        chain = Chain.objects.create(name='Chain', start_date=chain_start_date,
                                     owner=self.manager)
        deadline = chain_start_date + datetime.timedelta(days=3)
        first_task = Task.objects.create(worker=self.designer, task='Design',
                                         deadline=deadline, chain=chain,
                                         order=Task.FIRST_TASK)
        self.assertEqual(first_task.days_quantity_after_deadline(), 2)
        self.assertEqual(first_task.remaining_days(), None)


class ExpendedDaysTest(TaskTest):
    """Тестирует определение количества дней, затраченных на задачу."""
    def test_wait(self):
        """Тестирует случай, когда задача ожидает начала работы."""
        today = datetime.date.today()
        chain_start_date = today + datetime.timedelta(days=1)
        chain = Chain.objects.create(name='Chain', start_date=chain_start_date,
                                     owner=self.manager)
        deadline = chain_start_date + datetime.timedelta(days=3)
        first_task = Task.objects.create(worker=self.designer, task='Design',
                                         deadline=deadline, chain=chain,
                                         order=Task.FIRST_TASK)
        self.assertEqual(first_task.expended_days(), 0)

    def test_work(self):
        """Тестирует случай, когда задача работает."""
        today = datetime.date.today()
        chain_start_date = today - datetime.timedelta(days=4)
        chain = Chain.objects.create(name='Chain', start_date=chain_start_date,
                                     owner=self.manager)
        deadline = chain_start_date + datetime.timedelta(days=3)
        first_task = Task.objects.create(worker=self.designer, task='Design',
                                         deadline=deadline, chain=chain,
                                         status=Task.DONE_STATUS,
                                         finish_date=today,
                                         order=Task.FIRST_TASK)
        self.assertEqual(first_task.expended_days(), 5)

    def test_done(self):
        """Тестирует случай, когда задача завершена."""
        today = datetime.date.today()
        chain_start_date = today - datetime.timedelta(days=1)
        chain = Chain.objects.create(name='Chain', start_date=chain_start_date,
                                     owner=self.manager)
        deadline = chain_start_date + datetime.timedelta(days=3)
        first_task = Task.objects.create(worker=self.designer, task='Design',
                                         deadline=deadline, chain=chain,
                                         status=Task.DONE_STATUS,
                                         finish_date=today,
                                         order=Task.FIRST_TASK)
        self.assertEqual(first_task.expended_days(), 2)

    def test_stop(self):
        """Тестирует случай, когда задача остановлена."""
        today = datetime.date.today()
        chain_start_date = today - datetime.timedelta(days=1)
        chain = Chain.objects.create(name='Chain', start_date=chain_start_date,
                                     owner=self.manager)
        deadline = chain_start_date + datetime.timedelta(days=3)
        first_task = Task.objects.create(worker=self.designer, task='Design',
                                         deadline=deadline, chain=chain,
                                         status=Task.STOP_STATUS,
                                         order=Task.FIRST_TASK)
        self.assertEqual(first_task.expended_days(), None)
