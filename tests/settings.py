import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = (
    'todo',
    'pytils',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
)

ROOT_URLCONF = 'tests.urls'

AUTH_PROFILE_MODULE = 'todo.StaffProfile'

BASE_PATH = os.path.dirname(os.path.dirname(__file__))
TEST_DISCOVERY_ROOT = os.path.join(BASE_PATH, 'tests')

TEST_RUNNER = 'tests.runner.DiscoveryDjangoTestSuiteRunner'
