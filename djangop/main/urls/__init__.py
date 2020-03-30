from django.conf.urls import url
from django.contrib import admin

from main import views

admin.autodiscover()
urlpatterns = [
    # Site
    url(r'^$', views.index),
    url(r'^account/$', views.account),
    url(r'^chat/(?P<room_name>[^/]+)/$', views.room, name='room'),
    url(r'^chat/$', views.chat),
    url(r'^deposit/$', views.deposit),
    url(r'^depositmade/$', views.deposit_made),
    url(r'^forumactivity/$', views.forum_activity),
    url(r'^howtoplay/$', views.how_to_play),

    url(r'^signup/$', views.signup),
    url(r'^sitelogin/$', views.site_login),
    url(r'^sitelogout/$', views.site_logout),
]

# urlpatterns = format_suffix_patterns(urlpatterns)