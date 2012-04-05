from django.db import models
from django.contrib.auth.models import User


class Chain(models.Model):
    """Цепочка задач."""
    name = models.TextField()


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

    # Core fields.
    worker = models.ForeignKey(User)
    task = models.TextField()
    deadline = models.DateTimeField()
    # Metadata.
    finish_date = models.DateTimeField()
    status = models.IntegerField(choices=STATUS_CHOICES,
                                 default=UNCERTAIN_STATUS)
    chain = models.ForeignKey(Chain)
    order = models.IntegerField()

    def __unicode__(self):
        return self.task
