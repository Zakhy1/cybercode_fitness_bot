import os

from celery import Celery

# Установить модуль с настройками. Должна идти до следующей строчки
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')

# Позволит создавать настройки для celery в settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Сканирует все приложения и ищет файл tasks.py
app.autodiscover_tasks()

# app.conf.beat_schedule = {
#     'worktime': {
#         'task': 'apps.main.tasks.create_worktime_data',
#         'schedule': 30,
#     },
# 'scales_control': {
#     'task': 'apps.main.tasks.create_scales_control_data',
#     'schedule': 30,
# },
# }
