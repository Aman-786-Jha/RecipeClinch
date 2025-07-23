import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'starclinch.settings')

app = Celery('starclinch')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()



#### for the schedule purpose..beat
from celery.schedules import crontab

app.conf.beat_schedule = {
    'export-users-to-s3-weekly': {
        'task': 'apis.recipemodel.scheduled_tasks.export_users_to_s3',  
        'schedule': crontab(hour=3, minute=0, day_of_week='monday'),  
    },
}
