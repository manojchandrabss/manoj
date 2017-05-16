import sys

from .common import *

DEBUG = True
ENVIRONMENT = 'development'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'webpr_dev',
        'USER': 'webpr_user',
        'PASSWORD': 'manager',
        'HOST': 'postgres',
        'PORT': '5432',
    }
}

INSTALLED_APPS += (
    'django_extensions',
    'opbeat.contrib.django',
)

# opbeat integration
OPBEAT = {
    'ORGANIZATION_ID': 'da403e65570b4b8698b4d792008ba8f4',
    'APP_ID': '586cbb38c5',
    'SECRET_TOKEN': 'a8fae1043a8cae0a525787ed6cd6b76c84fbc723',
}

# Stripe Configuration
# TODO: setup stripe params
# STRIPE_SECRET_KEY = "sk_test_secret_key"
# STRIPE_PUBLIC_KEY = "pk_test_public key"

# Django Storages S3
AWS_S3_ACCESS_KEY_ID = 'AKIAJ6A4R4DR7J4IRIMQ'
AWS_S3_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'webpr-development'

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
SEMANTRIA_CONF_ID = '84d3f235-2406-4c5c-86d8-aed7660a370a'

# disable django DEBUG if we run celery worker
if 'celery' in sys.argv:
    DEBUG = False
