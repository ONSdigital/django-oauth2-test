# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from json import loads
from sh import git
import logging                                                      # Python logging package

stdlogger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'apps.accounts',
    'apps.credentials',
    'apps.information',
    'apps.tokens',
    'apps.web',
)

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# This specifies what version and application name is displayed  in the info endpoint. (i.e. http://localhost:8008/info)
# It also tries to detect the git_info file that is injected by jenkins in cloud foundry. If it's not there is uses
# values from the local system.

APPLICATION_NAME = 'oauth2 server'
APPLICATION_VERSION = '0.1.2'

# A global dictionary used to display info on the /info endpoint
MICRO_SERVICE_INFO = {
    "branch": "",
    "built": "N/A",
    "commit": "",
    "name": APPLICATION_NAME,
    "origin": "",
    "version": APPLICATION_VERSION
}

# if we can detect the git_info file then pull values from the file. Otherwise load values from the system we are
# currently running on.
if os.path.isfile('git_info'):
    with open('git_info') as micro_service_info_file:
        stdlogger.info("Found git_info. Configuring information endpoint for the OAuth2 server")
        micro_service_info_dictionary = loads(micro_service_info_file.read())
        MICRO_SERVICE_INFO['branch'] = micro_service_info_dictionary['branch']
        MICRO_SERVICE_INFO['built'] = micro_service_info_dictionary['built']
        MICRO_SERVICE_INFO['commit'] = micro_service_info_dictionary['commit']
        MICRO_SERVICE_INFO['origin'] = micro_service_info_dictionary['origin']
else:
    stdlogger.info("No git_info found. Detecting git local settings for the OAuth2 server")
    MICRO_SERVICE_INFO['branch'] = str(git('rev-parse', '--abbrev-ref', 'HEAD')).strip('\n')
    MICRO_SERVICE_INFO['commit'] = str(git('rev-parse', 'HEAD')).strip('\n')
    MICRO_SERVICE_INFO['origin'] = str(git('config', '--get', 'remote.origin.url')).strip('\n')





TIME_ZONE = 'UTC'

ROOT_URLCONF = 'proj.urls'

WSGI_APPLICATION = 'proj.wsgi.application'

ALLOWED_HOSTS = '*'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'proj', 'static'),
)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Used by whitenoise to speed up serving of static content.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'proj', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'EXCEPTION_HANDLER': 'proj.exceptions.custom_exception_handler',
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}


# Custom logging to give us unique logging to work on remote containers and normal logging
# Requirements for our custom loggers are:
# 1)    A console logger that logs debug to console for DEBUG=TRUE and WARNINGS and higher when DEBUG=FALSE.
# 2)    Disable all email sent to ADMINS via the mail_admins handler for the django.request and django.security loggers.
# 3)    Add two custom logging formatters to enhance the logging output.
# 4)    Add handlers to write files for 'proj' and 'app' name space. For production (DEBUG=FALSE) and dev (DEBUG=TRUE).
# 5)    Add LOGGERS for 'apps' and 'proj' name space. Add LOGGERS for python and django default. Add a logger for remote
#       files.

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,                                       # This disables existing django loggers
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s','datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s','datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'ons': {
            'format': ' {"created":"%(asctime)s", "service":"oauth2", "level": "%(levelname)s", "event":"%(message)s", "context": "%(name)s.%(funcName)s:%(lineno)d"  }','datefmt': '%Y-%m-%d %H:%M:%S '
        },

    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            #'filters': [],                      # Allow all logs to pass to console
            'class': 'logging.StreamHandler',
            'formatter': 'ons'
        },
        'console_cloud_foundry': {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'ons'
        },

        'development_logfile': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': 'oauth2_development.log',
            'formatter': 'verbose'
        },
        'production_logfile': {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'logging.FileHandler',
            'filename': 'oauth2_production.log',
            'formatter': 'verbose'
        },
        'remote_logfile': {
            'level': 'DEBUG',
            'filters': ['require_debug_false', 'require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': 'oauth2_remote.log',
            'formatter': 'verbose'
        },
        'proj_logfile': {
            'level': 'DEBUG',
            #'filters': ['require_debug_false','require_debug_true'],
            'filters':[],                           # Allow all 'proj' related logs to be sent to this project folder
            'class': 'logging.FileHandler',
            'filename': 'oauth2_proj.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        # This is our main log handler. It catches all logs within apps.*.*
        'apps': {
            'handlers': ['console', 'console_cloud_foundry', 'production_logfile', 'development_logfile'],
            'level': 'DEBUG',
        },
        # This defines a handler for the namespace proj.*.*
        'proj': {
            'handlers': ['console', 'console_cloud_foundry', 'development_logfile', 'proj_logfile'],
        },
        # Our remote handler is used for logging anything we want to be logged while the app is running remotely
        'remote': {
            'handlers': ['console', 'remote_logfile'],
        },
        # This is our default django handler loggs
        'django': {
            'handlers': ['console', 'development_logfile', 'production_logfile'],
        },
        # This is our default warnings log
        'py.warnings': {
            'handlers': ['console', 'development_logfile'],
        },
    }
}





