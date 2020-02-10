<h1>Emerald Games Site</h1>
<b>Important! Need to update setup to include the changes that need to be made to required libraries</b>
<h3>Table of contents</h3>

1. Setup
2. Celery
3. Database
4. Important notes on dependencies (If project isn't working)

<h3>SECTION 1: Setup</h3>

Install all of the requirements.

<code>pip install -r requirements.txt</code>

See section <i>Important Notes on Dependencies</i> if there are problems with setup

<h3>SECTION 2: Celery</h3>
Celery is used for periodic tasks. As of writing this (Jan 12th 2019) it is used for aborting all matches that went
past their max_match_length. This is so players will have their money returned to them if an error occurs in a match
and the game does not abort.

Start celery:

<code>celery -A djangop worker --loglevel=info -P gevent</code>

Start celery beat:

<code>celery -A djangop beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler</code>


Celery also requires redis to be running, open ubuntu and run

<code>service redis-server start</code>


<h3>SECTION 3: Database</h3>

If the database has to be recreated and your getting a no such table error. Try the command:

<code>python manage.py migrate --run-syncdb</code>

<h3>Important Notes on Dependencies</h3>
<h4>Channel Layers</h4>
If there is an issue with channel layers remove the line importing Group. Replace
all lines that use group with the new format:

    # This example uses WebSocket consumer, which is synchronous, and so
    # needs the async channel layer functions to be converted.
    from asgiref.sync import async_to_sync
    class ChatConsumer(WebsocketConsumer):
    def connect(self):
        async_to_sync(self.channel_layer.group_add)("chat", self.channel_name)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("chat", self.channel_name)

<h4>Django Rest Framework</h4>
If there is an issue with djangorestframework... The version of djangorestframework doesn't work with this version of
django. There should be a folder provided with the modified package rest_framework. If you cant find it just ask for it.
This version should replace the one the environment.

<h4>Celery</h4>
If there is an issue with celery... There was a problem with celery before and I had modify it. Let me know if celery
isn't working.

<h4>Channels Presence</h4>
There was also an issue with channels_presence. It didn't work with the current version of channels and I had to modify
it.