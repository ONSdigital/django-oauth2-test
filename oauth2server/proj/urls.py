from django.conf.urls import include, url
from django.contrib import admin
import logging

stdlogger = logging.getLogger(__name__)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/', include('apps.tokens.urls', namespace='api_v1')),
    url(r'api/account/', include('apps.accounts.urls', namespace='api_account')),
    url(r'^web/', include('apps.web.urls', namespace='web')),
    url(r'^info/', include('apps.information.urls', namespace='api_info')),
]
