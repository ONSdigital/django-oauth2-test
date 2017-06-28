__author__ = 'nherriot'

import sys
import json
from proj.settings.default import *

remoteLogger = logging.getLogger('remote')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'tbd(pv7679n_w-t++*s_*oon&#v0ubhkxhzvlq51ko2+=dt*z#'           #TODO inject this variable on production

# Extract the database URI value from VCAP_SERVICES

if 'VCAP_SERVICES' in os.environ:
    remoteLogger.info('VCAP_SERVICES found in os.environ')
    decoded_config = json.loads(os.environ['VCAP_SERVICES'])
    for key, value in decoded_config.items():
        remoteLogger.debug("Inspecting key: {} with value: {}".format(str(key), str(value)))
        if decoded_config[key][0]['name'] == 'postgresql':
            creds = decoded_config[key][0]['credentials']
            uri = creds['uri']
            remoteLogger.info("Found postgres uri string in vcap settings")
            remoteLogger.info("Postgres DATABASE uri: {}".format(uri))

else:
    remoteLogger.info('VCAP_SERVICES NOT found in os.environ using default SQL database')
    #return os.environ.get('SQLALCHEMY_DATABASE_URI', 'postgresql://ras_frontstage_backup:password@localhost:5431/postgres')



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'cgklfudq',
        'USER': 'cgklfudq',
        'PASSWORD':'SUEHnEG5I42gCGKXzpgGQ2XT_cZ-PEzi',
        'HOST':'stampy.db.elephantsql.com',
        'PORT': '5432',
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
