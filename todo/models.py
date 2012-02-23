from django.db import models


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

    status = models.IntegerField(choices=STATUS_CHOICES, default=UNCERTAIN_STATUS)
    task = models.TextField()
    chain = models.ForeignKey(Chain)

    def __unicode__(self):
        return self.task
