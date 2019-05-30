from django.conf.urls import url
from django.contrib import admin

from main.views.dev import sandbox

admin.autodiscover()

urlpatterns = [
    url(r'^changemaxmatchlength/$', sandbox.change_max_match_length),
    url(r'^maxmatchlength/$', sandbox.max_match_length),
    url(r'^(?P<game>\w+)/$', sandbox.sandbox),
    url(r'^(?P<game>\w+)/home/$', sandbox.home),
    url(r'^(?P<game>\w+)/players/$', sandbox.players),
    url(r'^(?P<game>\w+)/matches/$', sandbox.matches),
    url(r'^(?P<game>\w+)/match/(?P<match>\w+)/$', sandbox.match),
    url(r'^(?P<game>\w+)/settings/$', sandbox.settings),
    url(r'^(?P<game>\w+)/matchtypes/$', sandbox.match_types),
    url(r'^(?P<game>\w+)/matchtype/(?P<match_type>\w+)', sandbox.match_type),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
