from django.conf.urls import url
from django.contrib import admin

from main.views import forum

admin.autodiscover()
urlpatterns = [
    url(r'^$', forum.index),
    url(r'^newthread/$', forum.newthread),
    url(r'^(?P<category>\w+)/$', forum.category),
    url(r'^(?P<category>\w+)/(?P<thread>.*)/$', forum.thread),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
