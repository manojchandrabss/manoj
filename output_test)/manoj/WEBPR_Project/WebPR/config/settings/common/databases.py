# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
# default settings for mdillon/postgis image

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'HOST': 'postgres',
        'PORT': '5432',
    }
}
