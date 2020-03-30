from django.conf.urls import url
from django.contrib import admin
from rest_framework_expiring_authtoken import views as expiringTokenViews

from main.views import api

admin.autodiscover()
urlpatterns = [
    url(r'^abortmatch/$', api.abort_match),
    url(r'^addbalance/$', api.add_balance), # N
    url(r'^addusertogroup/$', api.add_user_to_group),
    url(r'^authtoken/$', expiringTokenViews.obtain_expiring_auth_token),
    url(r'^createuser/$', api.create_user), # N
    url(r'^createusergroup/$', api.create_user_group),
    url(r'^endmatch/$', api.end_match),
    url(r'^getgame/$', api.get_game), # N
    url(r'^getmatch/$', api.get_match),
    url(r'^getuser/$', api.get_user), # N
    url(r'^getuser/(?P<username>\w+)/$', api.create_user), # N
    url(r'^payout/$', api.payout),
    url(r'^removebalance/$', api.remove_balance), # N
    url(r'^startmatch/$', api.start_match),
    url(r'^playerinfo/$', api.player_info),
]

# urlpatterns = format_suffix_patterns(urlpatterns)