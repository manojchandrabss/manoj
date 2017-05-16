# This is experimental Swagger support within our package

from .general import DJANGO_SITE_NAME

SWAGGER_SETTINGS = {
    'info': {
        'title': DJANGO_SITE_NAME,
    },
}
