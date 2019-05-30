
Table of contents:

SECTION 1: Setup
SECTION 2: Celery
SECTION 3: Database

SECTION 1: Setup

pip install all of the packages in requirements.txt. Some of these packages had to be modified so there are custom
versions of these packages. If there are errors follow the process below.

All of the packages for this project should be installed in the virtual environment.
If they aren't follow this process

Install the packages by running these commands:

pip install celery
pip install djangorestframework
pip install djangorestframework-expiring-authtoken
pip install django-celery-beat
pip install mysqlclient
pip install gevent
pip install channels
pip install channels_redis
pip install channels_presence

If there is an issue with djangorestframework... The version of djangorestframework doesn't work with this version of
django. There should be a folder provided with the modified package rest_framework. If you cant find it just ask for it.
This version should replace the one the environment.

If there is an issue with celery... There was a problem with celery before and I had modify it. Let me know if celery
isn't working.

There was also an issue with channels_presence. It didn't work with the current version of channels and I had to modify
it.

SECTION 2: Celery
Celery is used for periodic tasks. As of writing this (Jan 12th 2019) it is used for aborting all matches that went
past their max_match_length. This is so players will have their money returned to them if a an error occurs in a match
and the game does not abort.

Start celery:

celery -A djangop worker --loglevel=info -P gevent

Start celery beat.

celery -A djangop beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

Celery also requires redis to be running, open ubuntu and run

service redis-server start

SECTION 4: Database

If the database has to be recreated and your getting a no such table error. Try the command
python manage.py migrate --run-syncdb


test