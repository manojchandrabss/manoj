import djcelery

from kombu import Queue, Exchange

BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis'
CELERY_ACCEPT_CONTENT = ['pickle']
CELERYD_TASK_TIME_LIMIT = 60 * 60 * 3
CELERY_SEND_EVENTS = True
CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"
CELERY_REDIS_HOST = 'redis'
CELERY_REDIS_PORT = 6379
CELERY_REDIS_DB = 0

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


djcelery.setup_loader()
