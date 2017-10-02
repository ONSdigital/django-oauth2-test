__author__ = 'nherriot'

from proj.settings.default import *


# Standard instance of a logger with __name__. We are using this so that our root folder has our logger defined.
stdlogger = logging.getLogger(__name__)
stdlogger.info("*** Local settings are being used. ***")


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'this-needs-to-change'           #TODO inject this variable on production

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db',
#        'NAME': 'rich_test_db',
#        'USER': 'weekr',
#        'PASSWORD': '',
#        'HOST': 'localhost',
#    },
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'postgres',                                 # Or path to database file if using sqlite3.
        'USER': 'postgres',                                 # Not used with sqlite3.
        'PASSWORD': 'password',                            # Not used for developing
        'HOST': 'localhost',                                # Set to using the postgres SQL DB within our docker container. See docker-compose.yml
                                                            # for information on this within the ras-compose project on Github for ONSDigital
        'PORT': '5431',                                     # Set to the exposed endpoint via our docker-compose file. Normally it's 5432 for postgres
    }
}

DEBUG = True                                                # Set to false on Production

OAUTH2_SERVER = {
    'ACCESS_TOKEN_LIFETIME': 3600,
    'AUTH_CODE_LIFETIME': 3600,
    'REFRESH_TOKEN_LIFETIME': 3600,
    'IGNORE_CLIENT_REQUESTED_SCOPE': False,
    'SET_AUTH_USER_ACTIVE_ON_REGISTRATION':False,           # when a new oauth user is added they are set as active by default if flag is set as true

}


# This defined the max number of failed logins a user can have before the account is locked
MAX_FAILED_LOGINS = 10
