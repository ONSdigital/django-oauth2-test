"""
Admin module
"""
from django.contrib import admin
from .models import OAuthScope, OAuthRefreshToken, OAuthAccessToken, OAuthAuthorizationCode


admin.site.register(OAuthScope)
admin.site.register(OAuthRefreshToken)
admin.site.register(OAuthAccessToken)
admin.site.register(OAuthAuthorizationCode)

