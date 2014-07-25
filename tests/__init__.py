import os
import django

try:
    django.setup()
except AttributeError:
    pass

test_runner = None
old_config = None

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'


def setup():
    global test_runner
    global old_config
    from django.test.simple import DjangoTestSuiteRunner
    test_runner = DjangoTestSuiteRunner()
    test_runner.setup_test_environment()
    old_config = test_runner.setup_databases()


def teardown():
    test_runner.teardown_databases(old_config)
    test_runner.teardown_test_environment()
