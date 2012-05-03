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
                                         deadline=deadline, chain=chain)
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
                            deadline=deadline_first_task)
        deadline_second_task = deadline_first_task + datetime.timedelta(days=2)
        second_task = Task.objects.create(worker=self.programmer,
                                          task='Programming',
                                          deadline=deadline_second_task,
                                          chain=chain)
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
                                         deadline=deadline, chain=chain)
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
                            status=Task.DONE_STATUS)
        deadline_second_task = deadline_first_task + datetime.timedelta(days=2)
        second_task = Task.objects.create(worker=self.programmer,
                                          task='Programming',
                                          deadline=deadline_second_task,
                                          chain=chain)
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
                                         deadline=deadline, chain=chain)
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
                            deadline=deadline_first_task)
        deadline_second_task = deadline_first_task + datetime.timedelta(days=2)
        Task.objects.create(worker=self.programmer, task='Programming',
                            deadline=deadline_second_task, chain=chain)
        first_task = Task.objects.get(task='Design')
        second_task = Task.objects.get(task='Programming')
        self.assertEqual(second_task.start_date(), first_task.deadline)

    def test_work(self):
        """Тестирует дату начала работы задачи со статусом WORK.

        Дата начала задачи наступает на следующий день после окончания
        предыдущей задачи (DONE). Это условие верно и для задач со статусом
        DONE или STOP.
        """
        today = datetime.date.today()
        chain_start_date = today - datetime.timedelta(days=2)
        chain = Chain.objects.create(name='Chain', start_date=chain_start_date,
                                     owner=self.manager)
        deadline_first_task = chain_start_date + datetime.timedelta(days=3)
        Task.objects.create(worker=self.designer, task='Design', chain=chain,
                            deadline=deadline_first_task, finish_date=today,
                            status=Task.DONE_STATUS)
        deadline_second_task = deadline_first_task + datetime.timedelta(days=2)
        Task.objects.create(worker=self.programmer, task='Programming',
                            deadline=deadline_second_task, chain=chain)
        design_finish = Task.objects.get(task='Design').finish_date
        prog_start = Task.objects.get(task='Programming').start_date()
        self.assertEqual(prog_start, design_finish + datetime.timedelta(1))

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
                            deadline=deadline_first_task)
        deadline_second_task = deadline_first_task + datetime.timedelta(days=2)
        Task.objects.create(worker=self.programmer, task='Programming',
                            deadline=deadline_second_task, chain=chain)
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
                                         deadline=deadline, chain=chain)
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
                                         deadline=deadline, chain=chain)
        self.assertEqual(first_task.days_quantity_after_deadline(), 2)
        self.assertEqual(first_task.remaining_days(), None)

    def task_wait_overdue(self):
        """Просрочен дедлайн у ожидающей задачи из-за предыдущей задачи.

        Предыдущая задача превысила свой дедлайн и дедлайн текущей задачи.
        """

    def task_work_overdue(self):
        """Работающая задача превысила дедлайн."""

    def task_done_overdue(self):
        """Задача выполнена с превышением дедлайна."""

    def task_stop_overdue(self):
        """Просрочен дедлайн у остановленной задачи.

        Владелец цепочки не решил проблему остановки задачи.
        """


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
                                         deadline=deadline, chain=chain)
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
                                         finish_date=today)
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
                                         finish_date=today)
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
                                         status=Task.STOP_STATUS)
        self.assertEqual(first_task.expended_days(), None)


class DaysToStartTest(TaskTest):
    """Тестирует определение количества дней, оставшихся до начала задачи."""
    def test_start_date_greater_than_today_to_one_day(self):
        """Дата начала больше текущей даты на один день."""
        today = datetime.date.today()
        chain = factories.ChainFactory(
            start_date=today + datetime.timedelta(days=1)
        )
        task = factories.TaskFactory(
            deadline=chain.start_date + datetime.timedelta(days=5),
            chain=chain
        )
        self.assertEqual(task.days_to_start(), 0)

    def test_today_equal_start_date(self):
        """Текущая дата совпадает с датой начала работы над задачей."""
        today = datetime.date.today()
        chain = factories.ChainFactory(start_date=today)
        task = factories.TaskFactory(
            deadline=chain.start_date + datetime.timedelta(days=5),
            chain=chain
        )
        self.assertIsNone(task.days_to_start())

    def test_prev_task_overdue(self):
        """Предыдущая задача превысила дедлайн."""
        today = datetime.date.today()
        chain = factories.ChainFactory(
            start_date=today - datetime.timedelta(days=7)
        )
        design = factories.TaskFactory(
            deadline=chain.start_date + datetime.timedelta(days=5),
            chain=chain
        )
        layout = factories.TaskFactory(
            deadline=design.deadline + datetime.timedelta(days=5),
            chain=chain
        )
        self.assertIsNone(layout.days_to_start())

    def test_task_not_wait(self):
        """Задача не ожидает начала работы, а имеет статус WORK/DONE/STOP."""
        today = datetime.date.today()
        chain = factories.ChainFactory(
            start_date=today - datetime.timedelta(days=3)
        )
        task = factories.TaskFactory(
            deadline=chain.start_date + datetime.timedelta(days=5),
            chain=chain
        )
        # WORK.
        self.assertIsNone(task.days_to_start())

        # STOP.
        task.status = task.STOP_STATUS
        self.assertIsNone(task.days_to_start())

        # DONE.
        task.status = task.DONE_STATUS
        task.finish_date = today
        self.assertIsNone(task.days_to_start())


class DurationTest(TestCase):
    """Тестирует определение количества дней, выделенных на выполнение задачи.
    """
    def setUp(self):
        """Создает две задачи. Первой выделено 3 дня, второй 2 дня.

        Например, первая задача ограничена сроком [2; 5), вторая -- [5; 7)
        """
        today = datetime.date.today()
        chain = factories.ChainFactory(start_date=today)
        self.first_task = factories.TaskFactory(
            deadline=chain.start_date + datetime.timedelta(days=3),
            chain=chain
        )
        self.second_task = factories.TaskFactory(
            deadline=self.first_task.deadline + datetime.timedelta(days=2),
            chain=chain
        )

    def test_first_task_in_chain(self):
        """Задача стоит первой в цепочке."""
        self.assertEqual(self.first_task.duration(), 3)

    def test_second_task_in_chain(self):
        """Задача стоит второй в цепочке."""
        self.assertEqual(self.second_task.duration(), 2)


class ChainActualStatusTest(TestCase):
    """Тестирует определение фактического статуса цепочки задач."""
    def setUp(self):
        factories.make_fixtures()

    def test_chain_wait(self):
        """Цепочка ожидает начала работы."""
        chain = Chain.objects.get(name='Chain waits')
        self.assertEqual(chain.actual_status(), Chain.WAIT_STATUS)

    def test_chain_work(self):
        """Цепочка работает."""
        chain = Chain.objects.get(name='Chain works')
        self.assertEqual(chain.actual_status(), Chain.WORK_STATUS)

    def test_chain_stop(self):
        """Цепочка остановлена."""
        chain = Chain.objects.get(name='Chain was stopped')
        self.assertEqual(chain.actual_status(), Chain.STOP_STATUS)

    def test_chain_done(self):
        """Цепочка завершена."""
        chain = Chain.objects.get(name='Chain was completed in time')
        self.assertEqual(chain.actual_status(), Chain.DONE_STATUS)
