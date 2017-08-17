from django.conf.urls import url

from apps.tokens.views import TokensView
from apps.accounts.views import AccountView
from apps.information.views import InformationView
from apps.analytics.views import AnalyticsView

urlpatterns = [
    url('^', InformationView.as_view(), name='information'),
]
