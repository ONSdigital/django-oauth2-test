from django.conf.urls import include, url

from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/', include('apps.tokens.urls', namespace='api_v1')),
    url(r'^web/', include('apps.web.urls', namespace='web')),
]