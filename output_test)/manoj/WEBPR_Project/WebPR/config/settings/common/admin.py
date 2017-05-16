# Django Suit Admin backend configuration
from .general import DJANGO_SITE_NAME

SUIT_CONFIG = {
    'ADMIN_NAME': DJANGO_SITE_NAME,
    'HEADER_DATE_FORMAT': 'l, j. F Y',
    'HEADER_TIME_FORMAT': 'H:i',
    'SHOW_REQUIRED_ASTERISK': True,
    'CONFIRM_UNSAVED_CHANGES': True,
    'MENU_EXCLUDE': ('authtoken', 'auth'),
    'MENU_OPEN_FIRST_CHILD': True,
}
