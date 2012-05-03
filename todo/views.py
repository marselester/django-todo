# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from todo.models import Chain, Task


@login_required
def actual_tasks(request):
    """Отображает список актуальных задач для исполнителя."""
    user = request.user
    actual_tasks = Task.objects.by_worker(user).actual()
    return render(request, 'todo/task_list.html', {
        'place': 'tasks',
        'actual_tasks': actual_tasks,
    })


@login_required
def task_detail(request, task_id):
    """Отображает описание задачи для исполнителя."""
    task = get_object_or_404(Task, pk=task_id)
    user = request.user
    if task.worker != user:
        return render(request, 'todo/error.html')
    actual_tasks = Task.objects.by_worker(user).actual()
    return render(request, 'todo/task_detail.html', {
        'current_task': task,
        'actual_tasks': actual_tasks,
    })


def task_archive(request):
    """Отображает архив задач для исполнителя."""
    return render(request, 'todo/task_archive.html')


@login_required
def actual_chains(request):
    """Отображает список актуальных цепочек задач для владельца."""
    user = request.user
    actual_chains = Chain.objects.by_owner(user).actual()
    return render(request, 'todo/chain_list.html', {
        'place': 'chains',
        'actual_chains': actual_chains,
    })


def chain_archive(request):
    """Отображает архив цепочек задач для владельца."""
    return render(request, 'todo/chain_archive.html')
