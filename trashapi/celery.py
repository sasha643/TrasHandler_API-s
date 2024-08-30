from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from trashapi import settings
from celery.schedules import crontab, schedule


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trashapi.settings')


app = Celery('trashapi')


app.conf.beat_schedule = {

    'refresh-tokens-every-10-minutes': {
        'task': 'api.tasks.refresh_tokens',
        'schedule': crontab(minute='*/10'),  # Run every minutes
    },

}

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

