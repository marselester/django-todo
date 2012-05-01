# -*- coding: utf-8 -*-
import datetime
import random

import factory
from django.contrib.auth.models import User

from todo.models import Chain, Task, StaffProfile


class StaffProfileFactory(factory.DjangoModelFactory):
    FACTORY_FOR = StaffProfile

    post = random.choice(('Дизайнер', 'Программист', 'Менеджер проектов'))
    user = None


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User

    username = factory.Sequence(lambda num: 'username{num}'.format(num=num))
    first_name = factory.Sequence(lambda num: 'Имя{num}'.format(num=num))
    last_name = factory.Sequence(lambda num: 'Фамилия{num}'.format(num=num))
    email = factory.LazyAttribute(lambda obj: '%s@example.org' % obj.username)
    is_staff = True
    is_active = True
    is_superuser = False
    password = '123'
    profile = factory.RelatedFactory(StaffProfileFactory, 'user')

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


class ChainFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Chain

    name = factory.Sequence(lambda num: 'Chain{num}'.format(num=num))
    owner = factory.SubFactory(UserFactory)


class TaskFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Task

    worker = factory.SubFactory(UserFactory)
    task = factory.Sequence(lambda num: 'Task{num}'.format(num=num))

    status = Task.UNCERTAIN_STATUS
    chain = factory.SubFactory(ChainFactory)


def make_fixtures():
    # Staff.
    manager = UserFactory(
        username='alexander',
        first_name='Александр',
        last_name='Македонский',
        profile__post='Менеджер проектов'
    )
    designer = UserFactory(
        username='kazimir',
        first_name='Казимир',
        last_name='Малевич',
        profile__post='Дизайнер'
    )
    ui_engineer = UserFactory(
        username='andy',
        first_name='Энди',
        last_name='Уорхол',
        profile__post='Дизайнер-технолог'
    )
    web_app_developer = UserFactory(
        username='ada',
        first_name='Ада',
        last_name='Лавлейс',
        profile__post='Программист'
    )
    content_manager = UserFactory(
        username='homer',
        first_name='Гомер',
        last_name='',
        profile__post='Контент-менеджер'
    )

    today = datetime.date.today()

    # Chain waits.
    chain = ChainFactory(
        name='Chain waits',
        owner=manager,
        start_date=today + datetime.timedelta(days=1)
    )
    # First task is design for 5 days.
    design = TaskFactory(
        worker=designer,
        deadline=chain.start_date + datetime.timedelta(days=5),
        chain=chain
    )
    # Second task is layout for 2 days.
    layout = TaskFactory(
        worker=ui_engineer,
        deadline=design.deadline + datetime.timedelta(days=2),
        chain=chain
    )
    # Third task is core for 4 days.
    core = TaskFactory(
        worker=web_app_developer,
        deadline=layout.deadline + datetime.timedelta(days=4),
        chain=chain
    )
    # Fourth task is content for 1 day.
    TaskFactory(
        worker=content_manager,
        deadline=core.deadline + datetime.timedelta(days=1),
        chain=chain
    )

    # Chain works 3 days.
    chain = ChainFactory(
        name='Chain works',
        owner=manager,
        start_date=today - datetime.timedelta(days=2)
    )
    # First task is design for 3 days.
    design = TaskFactory(
        worker=designer,
        deadline=chain.start_date + datetime.timedelta(days=3),
        chain=chain
    )
    # Second task is layout for 2 days.
    layout = TaskFactory(
        worker=ui_engineer,
        deadline=design.deadline + datetime.timedelta(days=2),
        chain=chain
    )
    # Third task is core for 4 days.
    core = TaskFactory(
        worker=web_app_developer,
        deadline=layout.deadline + datetime.timedelta(days=4),
        chain=chain
    )
    # Fourth task is content for 1 day.
    TaskFactory(
        worker=content_manager,
        deadline=core.deadline + datetime.timedelta(days=1),
        chain=chain
    )

    # Chain was completed in time.
    chain = ChainFactory(
        name='Chain was completed in time',
        owner=manager,
        start_date=today - datetime.timedelta(days=50)
    )
    # First task is design for 2 days.
    design = TaskFactory(
        worker=designer,
        deadline=chain.start_date + datetime.timedelta(days=2),
        chain=chain,
        status=Task.DONE_STATUS,
    )
    design.finish_date = design.deadline - datetime.timedelta(days=1)
    design.save()
    # Second task is layout for 2 days.
    layout = TaskFactory(
        worker=ui_engineer,
        deadline=design.deadline + datetime.timedelta(days=2),
        chain=chain,
        status=Task.DONE_STATUS,
    )
    layout.finish_date = layout.deadline - datetime.timedelta(days=1)
    layout.save()
    # Third task is core for 2 days.
    core = TaskFactory(
        worker=web_app_developer,
        deadline=layout.deadline + datetime.timedelta(days=2),
        chain=chain,
        status=Task.DONE_STATUS,
    )
    core.finish_date = core.deadline - datetime.timedelta(days=1)
    core.save()
    # Fourth task is content for 2 days.
    content = TaskFactory(
        worker=content_manager,
        deadline=core.deadline + datetime.timedelta(days=2),
        chain=chain,
        status=Task.DONE_STATUS,
    )
    content.finish_date = content.deadline - datetime.timedelta(days=1)
    content.save()

    # Chain is overdue.
    chain = ChainFactory(
        name='Chain is overdue',
        owner=manager,
        start_date=today - datetime.timedelta(days=666)
    )
    # First task is design for 2 days.
    design = TaskFactory(
        worker=designer,
        deadline=chain.start_date + datetime.timedelta(days=2),
        chain=chain,
        status=Task.DONE_STATUS,
    )
    design.finish_date = design.deadline - datetime.timedelta(days=1)
    design.save()
    # Second task is layout for 2 days.
    layout = TaskFactory(
        worker=ui_engineer,
        deadline=design.deadline + datetime.timedelta(days=2),
        chain=chain,
        status=Task.DONE_STATUS,
    )
    layout.finish_date = layout.deadline - datetime.timedelta(days=1)
    layout.save()
    # Third task is core for 2 days.
    core = TaskFactory(
        worker=web_app_developer,
        deadline=layout.deadline + datetime.timedelta(days=2),
        chain=chain,
        status=Task.DONE_STATUS,
    )
    core.finish_date = core.deadline - datetime.timedelta(days=1)
    core.save()
    # Fourth task is content for 2 days.
    content = TaskFactory(
        worker=content_manager,
        deadline=core.deadline + datetime.timedelta(days=2),
        chain=chain,
        status=Task.DONE_STATUS,
    )
    content.finish_date = content.deadline
    content.save()

    # Chain was stopped.
    chain = ChainFactory(
        name='Chain was stopped',
        owner=manager,
        start_date=today - datetime.timedelta(days=2)
    )
    # First task is design for 5 days.
    design = TaskFactory(
        worker=designer,
        deadline=chain.start_date + datetime.timedelta(days=5),
        chain=chain,
        status=Task.STOP_STATUS,
    )
    # Second task is layout for 2 days.
    layout = TaskFactory(
        worker=ui_engineer,
        deadline=design.deadline + datetime.timedelta(days=2),
        chain=chain,
    )

if __name__ == '__main__':
    Task.objects.all().delete()
    Chain.objects.all().delete()
    StaffProfile.objects.all().delete()
    User.objects.all().delete()

    make_fixtures()
