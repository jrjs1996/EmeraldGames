from django.contrib import admin

from main.views import dev

admin.autodiscover()
from django.conf.urls import url, include

urlpatterns = [
    url(r'^account/$', dev.account),
    url(r'^account/changecompanyname/$', dev.change_company_name),
    url(r'^account/companyname/$', dev.company_name),
    url(r'^games/$', dev.games),
    url(r'^home/$', dev.developers_home),
    url(r'^reference/$', dev.reference),
    url(r'^reference/item/(?P<item>\w+)/$', dev.reference_item),
    url(r'^sandbox/', include('main.urls.dev.sandbox', )),
    url(r'^signup/$', dev.signup),
    url(r'^tutorials/console/$', dev.console_tutorial),

]

# urlpatterns = format_suffix_patterns(urlpatterns)
