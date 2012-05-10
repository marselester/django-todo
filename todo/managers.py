# -*- coding: utf-8 -*-
from django.db.models.query import QuerySet


class ChainQuerySet(QuerySet):
    def by_owner(self, owner):
        """Возвращает цепочки владельца."""
        return self.filter(owner=owner)

    def actual(self):
        """Возвращает актуальтуные цепочки задач."""
        return self.filter(archive=False).order_by('start_date')


class TaskQuerySet(QuerySet):
    def by_worker(self, worker):
        """Возвращает задачи, которые нужно выполнить пользователю."""
        return self.filter(worker=worker)

    def actual(self):
        """Возвращает актуальные задачи."""
        return self.filter(archive=False).order_by('deadline')
