import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = (
    'todo',
    'django.contrib.contenttypes',
    'django.contrib.auth',
)

AUTH_PROFILE_MODULE = 'todo.StaffProfile'

BASE_PATH = os.path.dirname(os.path.dirname(__file__))
TEST_DISCOVERY_ROOT = os.path.join(BASE_PATH, 'tests')

TEST_RUNNER = 'tests.runner.DiscoveryDjangoTestSuiteRunner'
