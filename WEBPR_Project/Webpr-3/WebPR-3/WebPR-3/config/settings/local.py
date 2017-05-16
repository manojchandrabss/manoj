from .common import *

DEBUG = True
ENVIRONMENT = 'development'

INTERNAL_IPS = (
    '0.0.0.0',
    '127.0.0.1',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'webpr_dev',
        'USER': 'postgres',
        'PASSWORD': 'dbadmin',
        'HOST': 'postgres',
        'PORT': '5432',
    }
}

INSTALLED_APPS += (
    'django_extensions',
    'raven.contrib.django.raven_compat'
)

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SEMANTRIA_CONF_ID = '84d3f235-2406-4c5c-86d8-aed7660a370a'
