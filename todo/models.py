from datetime import datetime

from django.db import models
from django.contrib.auth.models import User


class Chain(models.Model):
    """Цепочка задач."""
    name = models.TextField()
    start_date = models.DateTimeField()
    priority = models.IntegerField(default=0)
    owner = models.ForeignKey(User)

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
    deadline = models.DateTimeField()
    # Metadata.
    finish_date = models.DateTimeField(null=True)
    status = models.IntegerField(choices=STATUS_CHOICES,
                                 default=UNCERTAIN_STATUS)
    chain = models.ForeignKey(Chain)
    order = models.IntegerField()

    def __unicode__(self):
        return self.task

    def actual_status(self):
        """Определяет фактический статус задачи."""
        if self.status in (self.DONE_STATUS, self.STOP_STATUS):
            return self.status
        if self.order == self.FIRST_TASK:
            if self.chain.start_date > datetime.now():
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
            if prev_task.deadline > datetime.now():
                start_date = prev_task.deadline
            else:
                start_date = None
        else:
            start_date = prev_task.finish_date
        return start_date
