from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from trashapi import settings
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trashapi.settings')


app = Celery('trashapi')
app.conf.beat_schedule = {
    'schedule-pickup-requests': {
        'task': 'api.tasks.schedule_pickup_requests',
        'schedule': crontab(minute='*', hour='*'),  # Runs every hour
    },
}
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

