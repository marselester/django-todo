# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from todo.models import Task


@login_required
def actual_tasks(request):
    """Отображает список актуальных задач для исполнителя."""
    user = request.user
    actual_tasks = Task.objects.by_worker(user).actual()
    return render(request, 'todo/task_list.html', {
        'place': 'tasks',
        'actual_tasks': actual_tasks,
    })


def task_detail(request, task_id):
    """Отображает описание задачи для исполнителя."""
    return render(request, 'todo/task_detail.html')


def task_archive(request):
    """Отображает архив задач для исполнителя."""
    return render(request, 'todo/task_archive.html')


def actual_chains(request):
    """Отображает список актуальных цепочек задач для владельца."""
    return render(request, 'todo/chain_list.html', {'place': 'chains'})


def chain_archive(request):
    """Отображает архив цепочек задач для владельца."""
    return render(request, 'todo/chain_archive.html')
