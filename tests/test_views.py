# -*- coding: utf-8 -*-
from django_webtest import WebTest

from django.core.urlresolvers import reverse

from . import factories


class ActualTasksTest(WebTest):
    def setUp(self):
        factories.make_fixtures()

    def test_user_not_logined(self):
        response = self.app.get(reverse('todo_actual_tasks'))
        self.assertEqual(response.status_int, 302)

    def test_designer_logined(self):
        response = self.app.get(reverse('todo_actual_tasks'), user='kazimir')
        assert 'Казимир Малевич' in response


class ActualChainsTest(WebTest):
    def setUp(self):
        factories.make_fixtures()

    def test_user_not_logined(self):
        response = self.app.get(reverse('todo_actual_chains'))
        self.assertEqual(response.status_int, 302)

    def test_manager_logined(self):
        response = self.app.get(reverse('todo_actual_chains'),
                                user='alexander')
        assert 'Александр Македонский' in response
