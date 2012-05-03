# -*- coding: utf-8 -*-
import datetime

from django.db import models
from django.contrib.auth.models import User
from model_utils.managers import PassThroughManager

from todo.managers import ChainQuerySet, TaskQuerySet


class Chain(models.Model):
    """Цепочка задач."""
    # Core fields.
    name = models.TextField()
    start_date = models.DateField()
    priority = models.IntegerField(default=0)
    # Metadata.
    owner = models.ForeignKey(User)
    archive = models.BooleanField(default=False)

    # Default manager.
    objects = PassThroughManager.for_queryset_class(ChainQuerySet)()

    def actual_status(self):
        """Определяет фактический статус цепочки."""
        if self.start_date > datetime.date.today():
            return Task.WAIT_STATUS
        if self.task_set.filter(status=Task.STOP_STATUS).exists():
            return Task.STOP_STATUS
        last_task = Task.objects.last_task_in_chain(self)
        if last_task.actual_status() == Task.DONE_STATUS:
            return Task.DONE_STATUS
        else:
            return Task.WORK_STATUS

    def deadline(self):
        """Определяет дедлайн цепочки."""

    def remaining_days(self):
        """Определяет количество дней, оставшихся до дедлайна последней задачи.
        """

    def days_quantity_after_deadline(self):
        """Определяет количество дней, на которые просрочена последняя задача.
        """

    def expended_days(self):
        """Определяет количество дней, затраченных на цепочку."""


class Task(models.Model):
    """Задача."""
    UNCERTAIN_STATUS = 0
    DONE_STATUS = 1
    STOP_STATUS = 2
    WAIT_STATUS = 3
    WORK_STATUS = 4
    STATUS_CHOICES = (
        (DONE_STATUS, 'done'),
        (STOP_STATUS, 'stop')
    )

    FIRST_TASK = 1

    # Core fields.
    worker = models.ForeignKey(User)
    task = models.TextField()
    deadline = models.DateField()
    # Metadata.
    finish_date = models.DateField(null=True)
    status = models.IntegerField(choices=STATUS_CHOICES,
                                 default=UNCERTAIN_STATUS)
    chain = models.ForeignKey(Chain)
    order = models.IntegerField()
    archive = models.BooleanField(default=False)

    # Default manager.
    objects = PassThroughManager.for_queryset_class(TaskQuerySet)()

    def __unicode__(self):
        return self.task

    def save(self, *args, **kwargs):
        # Расчитывает порядковый номер у новой задачи.
        if not self.pk:
            try:
                last_task = Task.objects.last_task_in_chain(self.chain)
                self.order = last_task.order + 1
            except self.DoesNotExist:
                self.order = self.FIRST_TASK
        super(Task, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('todo_task_detail', (), {'task_id': self.pk})

    def actual_status(self):
        """Определяет фактический статус задачи."""
        if self.status in (self.DONE_STATUS, self.STOP_STATUS):
            return self.status
        if self.order == self.FIRST_TASK:
            if self.chain.start_date > datetime.date.today():
                return self.WAIT_STATUS
            else:
                return self.WORK_STATUS
        prev_task = _prev_task(self)
        if prev_task.status == self.DONE_STATUS:
            return self.WORK_STATUS
        else:
            return self.WAIT_STATUS

    def start_date(self):
        """Определяет дату начала работы над задачей, если это возможно."""
        # Для первой задачи равна дате начала работы над цепочкой.
        if self.order == self.FIRST_TASK:
            return self.chain.start_date
        prev_task = _prev_task(self)
        # Для статуса WAIT равна дедлайну предыдущей задачи. Если дедлайн
        # просрочен, дата начала задачи не прогнозируема.
        # Для статусов WORK, DONE, STOP равна следующей дате, после окончания
        # предыдущей задачи.
        if self.actual_status() == self.WAIT_STATUS:
            if prev_task.deadline > datetime.date.today():
                start_date = prev_task.deadline
            else:
                start_date = None
        else:
            start_date = prev_task.finish_date + datetime.timedelta(days=1)
        return start_date

    def be_in_time(self):
        """Определяет, успевает ли задача к дедлайну."""
        return self.days_quantity_after_deadline() is None

    def days_to_start(self):
        """Определяет количество дней, оставшихся до начала работы над задачей.

        Например, задача ограничена сроком [26; 29) и сейчас 23 число.
        До начала работы осталось 2 полных дня, так как текущий день
        не учитывается.
        """
        start_date = self.start_date()
        today = datetime.date.today()
        if start_date is not None and start_date > today:
            time_to_start = start_date - today - datetime.timedelta(days=1)
            days_to_start = time_to_start.days
        else:
            days_to_start = None
        return days_to_start

    def remaining_days(self):
        """Определяет количество дней, оставшихся до дедлайна.

        Например, задача ограничена сроком [26; 29) и сейчас 27 число.
        До дедлайна остался 1 полный день (28 число), так как текущий день
        не учитывается.
        """
        today = datetime.date.today()
        if today < self.deadline:
            # Учитываем только полные дни
            time_remaining = self.deadline - today - datetime.timedelta(days=1)
            remaining_days = time_remaining.days
        else:
            remaining_days = None
        return remaining_days

    def days_quantity_after_deadline(self):
        """Определяет количество дней, на которые просрочена задача."""
        days_quantity = None
        today = datetime.date.today()
        if self.actual_status() == self.DONE_STATUS:
            # Задача завершена с превышением дедлайна.
            if self.finish_date >= self.deadline:
                time_after_deadline = (self.finish_date - self.deadline
                                       + datetime.timedelta(1))
                days_quantity = time_after_deadline.days
        # Задача со статусом WAIT/WORK/STOP превысила дедлайн.
        elif today >= self.deadline:
            time_after_deadline = today - self.deadline + datetime.timedelta(1)
            days_quantity = time_after_deadline.days
        return days_quantity

    def expended_days(self):
        """Определяет количество дней, затраченных на задачу."""
        status = self.actual_status()
        if status == self.WAIT_STATUS:
            expended_days = 0
        elif status == self.WORK_STATUS:
            today = datetime.date.today()
            expended_time = today - self.start_date() + datetime.timedelta(1)
            expended_days = expended_time.days
        elif status == self.DONE_STATUS:
            expended_time = (self.finish_date - self.start_date()
                             + datetime.timedelta(days=1))
            expended_days = expended_time.days
        else:
            expended_days = None
        return expended_days

    def duration(self):
        """Определяет количество дней, выделенных на выполнение задачи."""
        if self.order == self.FIRST_TASK:
            duration = self.deadline - self.chain.start_date
        else:
            prev_task = _prev_task(self)
            duration = self.deadline - prev_task.deadline
        return duration.days


def _prev_task(task):
    """Возвращает предыдущую задачу."""
    if task.order < Task.FIRST_TASK:
        raise Task.DoesNotExist
    order_prev_task = task.order - 1
    prev_task = Task.objects.get(chain=task.chain, order=order_prev_task)
    return prev_task


class StaffProfile(models.Model):
    """Профиль сотрудника."""
    user = models.ForeignKey(User, unique=True)

    post = models.TextField(max_length=45)

    def __unicode__(self):
        full_name = self.user.get_full_name()
        return u"{post} {full_name}".format(full_name=full_name,
                                            post=self.post)
