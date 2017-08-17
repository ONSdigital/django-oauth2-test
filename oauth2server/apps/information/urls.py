from django.conf.urls import url

from apps.information.views import InformationView

urlpatterns = [
    url('^', InformationView.as_view(), name='information'),
]
