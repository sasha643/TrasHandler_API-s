from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trashapi.settings')

app = Celery('trashapi')

# Load settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Celery Beat Schedule
app.conf.beat_schedule = {
    'refresh-tokens-every-5-minutes': {
        'task': 'api.tasks.refresh_tokens',
        'schedule': crontab(minute='*/5'),  # Run every 5 minutes
    },
}

# Discover tasks in Django apps
app.autodiscover_tasks()
