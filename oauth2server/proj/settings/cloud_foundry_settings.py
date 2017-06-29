__author__ = 'nherriot'

# This settings file is loaded when the system is run via cloud foundry. It's controlled by the manifest_develop_cloudfoundry.yml file in the root folder.
# Parameters used to make this settings file active are: DJANGO_SETTINGS_MODULE: proj.settings.cloud_foundry_settings.

import sys
import json

from proj.settings.default import *

remoteLogger = logging.getLogger('remote')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'tbd(pv7679n_w-t++*s_*oon&#v0ubhkxhzvlq51ko2+=dt*z#')


### Extract the database URI value from VCAP_SERVICES ###
# This will search for the env variable VCAP_SERVICES - which indicates we are running on Cloud Foundry. If this is
# the case we need to extract our dynamic DB settings so we know how to speak to our Postgres DB. We then override the
# DB settings of our server to use the Cloud Foundry dynamic values.
"""
    VCAP_SERVICES exmple:

    System-Provided:
        {
         "VCAP_SERVICES": {
          "rds": [
           {
            "credentials": {
             "db_name": "dbfkapanmvevuvb8f",
             "host": "mvp-applicationdb.cef6vnd8djsq.eu-central-1.rds.amazonaws.com",
             "password": "g7p3ljwzhto2mm19wkhb6gr8o",
             "uri": "postgres://uvbaf4yfdrflyap0:g7p3ljwzhto2mm19wkhb6gr8o@mvp-applicationdb.cef6vnd8djsq.eu-central-1.rds.amazonaws.com:5432/dbfkapanmvevuvb8f",
             "username": "uvbaf4yfdrflyap0"
            },
            "label": "rds",
            "name": "oauth-db",
            "plan": "shared-psql",
            "provider": null,
            "syslog_drain_url": null,
            "tags": [
             "database",
             "RDS",
             "postgresql"
            ],
            "volume_mounts": []
           }
          ]
         }
        }

"""

if 'VCAP_SERVICES' in os.environ:
    remoteLogger.info('VCAP_SERVICES found in environment')
    vcap_config = json.loads(os.environ['VCAP_SERVICES'])

    for key, value in vcap_config.items():
        remoteLogger.info('Inspecting key: "' + str(key) + '" with value: ' + str(value))
        if vcap_config[key][0]['name'] == 'oauth-db':
            vcap_credentials = vcap_config[key][0]['credentials']
            DB_HOST = vcap_credentials['host']
            DB_NAME = vcap_credentials['db_name']
            DB_USERNAME = vcap_credentials['username']
            DB_PASSWORD = vcap_credentials['password']
            remoteLogger.info('Postgres DATABASE found ')
        else:
            DB_HOST = vcap_credentials['host']
            DB_NAME = vcap_credentials['postgres']
            DB_USERNAME = vcap_credentials['postgres']
            DB_PASSWORD = vcap_credentials['password']
            remoteLogger.info('VCAP_SERVICES defined but no URI credential found. Using Defaults')
else:
    DB_HOST = 'stampy.db.elephantsql.com'
    DB_NAME = 'cgklfudq'
    DB_USERNAME = 'cgklfudq'
    DB_PASSWORD = 'SUEHnEG5I42gCGKXzpgGQ2XT_cZ-PEzi'
    remoteLogger.info('VCAP_SERVICES NOT found in environment. Using Test Environment')


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#        'NAME': 'postgres',                                 #TODO inject this in production.
        'NAME': DB_NAME,
#        'USER': 'postgres',                                 #TODO inject this in production.
        'USER': DB_USERNAME,
        #'PASSWORD': 'postgres',                             #TODO inject this in production.
        'PASSWORD':DB_PASSWORD,
        #'HOST': 'postgres',                                 # Set to using the postgres SQL DB within our docker container. See docker-compose.yml
                                                              # for information on this within the ras-compose project on Github for ONSDigital
        'HOST':DB_HOST,
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
