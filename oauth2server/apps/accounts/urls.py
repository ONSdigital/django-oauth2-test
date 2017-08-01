from django.conf.urls import url

from apps.accounts.views import AccountView


urlpatterns = [
    url('^create/?', AccountView.as_view(), name='account'),
#    url('^activate/?', AccountActivateView.as_view(), name='account_activate' ),

]
