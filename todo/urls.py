from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('todo.views',
    url(r'^$', 'actual_tasks', name='todo_actual_tasks'),
    url(r'^task/archive/$', 'task_archive', name='todo_task_archive'),
    url(r'^task/(?P<task_id>\d+)/$', 'task_detail', name='todo_task_detail'),
)
