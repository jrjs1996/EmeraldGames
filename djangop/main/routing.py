from django.conf.urls import url

from main.consumers.Consumers import PlayerConsumer, ControllerConsumer

websocket_urlpatterns = [
    url(r'^ws/sandbox/player/$', PlayerConsumer),
    url(r'^ws/sandbox/controller/$', ControllerConsumer)
]


