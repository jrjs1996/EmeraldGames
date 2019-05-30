start celery -A djangop worker --loglevel=info -P gevent
start celery -A djangop beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler