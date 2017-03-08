"""
Admin module
"""
from django.contrib import admin
from .models import OAuthUser, OAuthClient


admin.site.register(OAuthClient)
admin.site.register(OAuthUser)

