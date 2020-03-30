from django.conf.urls import url
from django.contrib import admin

from main.views import sandbox

admin.autodiscover()
urlpatterns = [
    url(r'^abortmatch/$', sandbox.abort_match),
    url(r'^addplayertogroup/$', sandbox.add_player_to_group),
    url(r'^authtoken/$', sandbox.obtain_auth_token),
    url(r'^creatematch/$', sandbox.create_match),
    url(r'^createplayergroup/$', sandbox.create_player_group),
    url(r'^endmatch/$', sandbox.end_match),
    url(r'^matchinfo/$', sandbox.match_info),
    url(r'^playerinfo/$', sandbox.player_info),
    url(r'^startmatch/$', sandbox.start_match),
    url(r'^playerquit/$', sandbox.player_quit),
    url(r'^createsoloplayergroup/$', sandbox.create_solo_player_group),
    url(r'^removeplayergroup/$', sandbox.remove_player_group)
]