# -----------------------------------------------------------------------------
# General Django Configuration Starts Here
# -----------------------------------------------------------------------------

from .general import *
from .paths import *
from .security import *
from .installed_apps import *
from .authentication import *
from .internationalization import *
from .middleware import *
from .templates import *
from .databases import *
from .static import *
from .logging import *
# storage configuration (aws s3 etc)
from .storage import *
# email and sms notifications (twilio)
from .notifications import *
# PDF rendering default settings
from .pdf import *
# cors headers exposed
from .cors import *

# -----------------------------------------------------------------------------
# Installed Django Apps Configuration Starts Here
# -----------------------------------------------------------------------------
# Allauth - auth app with battaries included
from .allauth import *
# Django Suite Configuration (Admin replacement for Django Admin)
from .admin import *
# Caching Framework (Cacheops)
from .cacheops import *
# Payment Configuration (Stripe)
from .payment import *
# swagger
from .swagger import *
# celery
from .celery import *



# -----------------------------------------------------------------------------
# Business Logic Custom Variables and Settings
# -----------------------------------------------------------------------------
from .business_logic import *

SITE_ID = 1
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

ADMINS = (
    # ('Dmitry Semenov', 'dmitry@saritasa.com'),
    # ('Roman Gorbil', 'gorbil@saritasa.com'),
    ('Vitold Komorovski', 'vitold@saritasa.com')
)

MANAGERS = ADMINS

CRISPY_TEMPLATE_PACK = 'bootstrap3'
