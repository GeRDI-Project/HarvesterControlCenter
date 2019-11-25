from hcc_py.settings import *  # noqa: F401, F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

INSTALLED_APPS.append('django_nose')

# Use nose to run all tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Tell nose to measure coverage on the required apps
NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=api, hcc_py',
]
