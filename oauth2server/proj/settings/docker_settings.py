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


# Extract the database URI value from VCAP_SERVICES


if 'VCAP_SERVICES' in os.environ:
    print('VCAP_SERVICES found in os.environ')
    decoded_config = json.loads(os.environ['VCAP_SERVICES'])
    for key, value in decoded_config.items():
        print('Inspecting key: "' + str(key) + '" with value: ' + str(value))
        if decoded_config[key][0]['name'] == 'postgresql':
            creds = decoded_config[key][0]['credentials']
            uri = creds['uri']
            print ('Found postgres uri string in vcap settings')
            print('Postgres DATABASE uri: ' + uri)



else:
    print('VCAP_SERVICES NOT found in os.environ using default SQL database')
    #return os.environ.get('SQLALCHEMY_DATABASE_URI', 'postgresql://ras_frontstage_backup:password@localhost:5431/postgres')



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#        'NAME': 'postgres',                                 #TODO inject this in production.
        'NAME': 'cgklfudq',
#        'USER': 'postgres',                                 #TODO inject this in production.
        'USER': 'cgklfudq',
        #'PASSWORD': 'postgres',                             #TODO inject this in production.
        'PASSWORD':'SUEHnEG5I42gCGKXzpgGQ2XT_cZ-PEzi',
        #'HOST': 'postgres',                                 # Set to using the postgres SQL DB within our docker container. See docker-compose.yml
                                                            # for information on this within the ras-compose project on Github for ONSDigital
        'HOST':'stampy.db.elephantsql.com',
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
