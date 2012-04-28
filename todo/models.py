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

    def deadline(self):
        """Определяет дедлайн цепочки."""


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

    def actual_status(self):
        """Определяет фактический статус задачи."""
        if self.status in (self.DONE_STATUS, self.STOP_STATUS):
            return self.status
        if self.order == self.FIRST_TASK:
            if self.chain.start_date > datetime.date.today():
                return self.WAIT_STATUS
            else:
                return self.WORK_STATUS
        order_prev_task = self.order - 1
        prev_task = Task.objects.get(chain=self.chain, order=order_prev_task)
        if prev_task.status == self.DONE_STATUS:
            return self.WORK_STATUS
        else:
            return self.WAIT_STATUS

    def start_date(self):
        """Определяет дату начала работы над задачей, если это возможно."""
        # Для первой задачи равна дате начала работы над цепочкой.
        if self.order == self.FIRST_TASK:
            return self.chain.start_date
        order_prev_task = self.order - 1
        prev_task = Task.objects.get(chain=self.chain, order=order_prev_task)
        # Для статуса WAIT равна дедлайну предыдущей задачи. Если дедлайн
        # просрочен, дата начала задачи не прогнозируема.
        # Для статусов WORK, DONE, STOP равна дате окончания предыдущей задачи.
        if self.actual_status() == self.WAIT_STATUS:
            if prev_task.deadline > datetime.date.today():
                start_date = prev_task.deadline
            else:
                start_date = None
        else:
            start_date = prev_task.finish_date
        return start_date

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
        today = datetime.date.today()
        if today >= self.deadline:
            time_after_deadline = today - self.deadline + datetime.timedelta(1)
            days_quantity = time_after_deadline.days
        else:
            days_quantity = None
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


class StaffProfile(models.Model):
    """Профиль сотрудника."""
    user = models.ForeignKey(User, unique=True)

    post = models.TextField(max_length=45)

    def __unicode__(self):
        full_name = self.user.get_full_name()
        return u"{post} {full_name}".format(full_name=full_name,
                                            post=self.post)
