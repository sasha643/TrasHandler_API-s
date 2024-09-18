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
    'track_accepted_pickups_morning': {
        'task': 'api.tasks.track_vendor_location_task',
        'schedule': crontab(minute='0-59', hour='11', day_of_week='*'),  # 11:00 AM to 12:00 PM IST
    },
    # Evening Slot: 5:00 PM - 6:00 PM IST
    'track_accepted_pickups_evening': {
        'task': 'api.tasks.track_vendor_location_task',
        'schedule': crontab(minute='0-59', hour='17', day_of_week='*'),  # 5:00 PM to 6:00 PM IST
    },

}

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

