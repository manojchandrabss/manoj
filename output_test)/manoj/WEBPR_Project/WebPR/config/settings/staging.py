from .common import *
from django.conf import settings
DEBUG = False
ENVIRONMENT = 'development'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'webpr_staging',
        'USER': 'webpr_staging',
        'PASSWORD': 'LJHldfkajsjFHsfuiwd',
        'HOST': 'rds-staging.aws.io',
        'PORT': '5432',
    }
}

# celery broker url
BROKER_URL = 'redis://redis.aws.io:6379/5'
CELERY_REDIS_HOST = 'redis.aws.io'
CELERY_RESULT_BACKEND = 'redis://redis.aws.io:6379/5'
CELERY_ACCEPT_CONTENT = ['pickle']
CELERYD_TASK_TIME_LIMIT = 3600 * 6
CELERYD_CONCURRENCY = 8
CELERY_SEND_EVENTS = True
CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"
CELERY_REDIS_PORT = 6379
CELERY_REDIS_DB = 5
# just remember to add to env
C_FORCE_ROOT="true"

CELERY_QUEUES = (
    Queue('webpr', Exchange('webpr'), routing_key='wptask'),
)
CELERY_ROUTES = {
    'apps.mentions.tasks.set_rating': {
        'queue': 'webpr',
        'routing_key': 'wptask',
    },
    'apps.mentions.tasks.analyze_mentions': {
        'queue': 'webpr',
        'routing_key': 'wptask',
    },
    'apps.mentions.tasks.get_query': {
        'queue': 'webpr',
        'routing_key': 'wptask',
    },
    'apps.mentions.tasks.recalculate_rating': {
        'queue': 'webpr',
        'routing_key': 'wptask',
    },
    'apps.mentions.tasks.clear_temporary_table': {
        'queue': 'webpr',
        'routing_key': 'wptask',
    },
    'apps.mentions.tasks.check_rating_date': {
        'queue': 'webpr',
        'routing_key': 'wptask',
    },
    'apps.mentions.tasks.bulk_merchant_import': {
        'queue': 'webpr',
        'routing_key': 'wptask',
    },
}
# Caching options
CACHEOPS_REDIS = {
    'host': 'redis.aws.io',
    'port': 6379,
    'db': 6,
    'socket_timeout': 5
}


INSTALLED_APPS += (
    'django_extensions',
)

settings.COMPRESS_ENABLED = True

# Stripe Configuration
# TODO: setup stripe params
# STRIPE_SECRET_KEY = "sk_test_secret_key"
# STRIPE_PUBLIC_KEY = "pk_test_public key"

# Django Storages S3
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_S3_ACCESS_KEY_ID = 'AKIAIGNN2MBXSTFPURFQ'
AWS_S3_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'webpr-staging'


# If you wish to use AWS S3 storage simply comment or remove the line below
# In this case storage params are defined by config/settings/commons/storage.py
# DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# SendGrid
# TODO: setup sendgrid params
SENDGRID_ID = 'KhENVZz5TSihOeHlCTkckw'
SENDGRID_KEY = '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'
SENDGRID_API_KEY = SENDGRID_KEY


# EMAIL Notification
# TODO: setup email params
EMAIL_HOST = 'smtp.sendgrid.net'
# EMAIL_HOST_USER = 'user_name'
# EMAIL_HOST_PASSWORD = 'password'
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# PUSH Notifications
# TODO: setup push notifications params
# PUSH_NOTIFICATIONS_SETTINGS = {
#     "GCM_API_KEY": "AIzaSyAej0Dw2Mcy2ppj_JpSwgY25yn6jpnKgp4",
#     "APNS_CERTIFICATE": BASE_DIR + "/app/certs/crtdev/cert.pem",
# }
SITE_ID = 1


PUSHER_APP_SETTINGS = {
    "app_id": "151067",
    "key": "c018434f98b07ab3edbc",
    "secret": '00014538703e7818fc0f',
    "ssl": True,
    "port": 443
}

# semantria config id, it depends on environment: staging, prod etc
SEMANTRIA_CONF_ID = 'fef58a7b7ae5899a161adc0d6ca09e2e'
