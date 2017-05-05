__author__ = 'nherriot'

import sys

from proj.settings.default import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'tbd(pv7679n_w-t++*s_*oon&#v0ubhkxhzvlq51ko2+=dt*z#'           #TODO inject this variable on production

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': 'django_oauth2_server',
#        'USER': '',
#        'PASSWORD': '',
#        'HOST': '',
#    },
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'postgres',                                 #TODO inject this in production.
        'USER': 'postgres',                                 #TODO inject this in production.
        #'PASSWORD': 'postgres',                             #TODO inject this in production.
        'HOST': 'postgres',                                 # Set to using the postgres SQL DB within our docker container. See docker-compose.yml
                                                            # for information on this within the ras-compose project on Github for ONSDigital
        'PORT': '5432',                                     # While running inside our docker container we use the normal port to access postgres
    }
}

DEBUG = True                                                # Set to false on Production

OAUTH2_SERVER = {
   'ACCESS_TOKEN_LIFETIME': 3600,
   'AUTH_CODE_LIFETIME': 3600,
   'REFRESH_TOKEN_LIFETIME': 3600,
   'IGNORE_CLIENT_REQUESTED_SCOPE': False,
}


# This defined the max number of failed logins a user can have before the account is locked
MAX_FAILED_LOGINS = 10
