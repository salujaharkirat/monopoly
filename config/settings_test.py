from config.settings import *

# CI has no .env, so settings.SECRET_KEY would be None and Django refuses to start.
SECRET_KEY = 'test-only-secret-key'

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
  }
}