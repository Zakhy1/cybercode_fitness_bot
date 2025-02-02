import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'notify': {
        'task': 'bot.tasks.remind_about_cheque',
        'schedule': crontab(hour=12, minute=0),
    },
}
