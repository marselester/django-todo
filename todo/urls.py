from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('todo.views',
    url(r'^$', 'actual_tasks', name='todo_actual_tasks'),
)
