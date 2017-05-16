# Application definition
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.gis',
    'cacheops',
    'corsheaders',
    'storages',
    'taggit',
    'imagekit',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'crispy_forms',
    'push_notifications',
    'djcelery',
    'django_hstore',
    'django_object_actions'
)

LOCAL_APPS = (
    'apps.users',
    'apps.mentions'
)

INSTALLED_APPS += LOCAL_APPS