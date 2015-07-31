"""
Django settings for annotationsx project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.contrib import messages
from secure import SECURE_SETTINGS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'eyc+bftd*fskn^_vt4+pr)0-ih+7sc%8i40*c=cji6*#+&2paj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_extensions',
    'django_jenkins',
    'bootstrap3',
    'crispy_forms',
    'ims_lti_py',
    'hx_lti_initializer',
    'hx_lti_assignment',
    'target_object_database',
    'django_auth_lti',
    'django_app_lti',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'annotationsx.middleware.XFrameOptionsMiddleware',
    #'django_auth_lti.middleware.LTIAuthMiddleware',
    #'django_auth_lti.middleware_patched.MultiLTILaunchAuthMiddleware'
)

ROOT_URLCONF = 'annotationsx.urls'

WSGI_APPLICATION = 'annotationsx.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'django_db',
# 	'USER': 'root',
# 	'PASSWORD': 'bu5egkeShy7Gphqf',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': SECURE_SETTINGS.get('db_default_name', 'annotationsx'),
        'USER': SECURE_SETTINGS.get('db_default_user', 'annotationsx'),
        'PASSWORD': SECURE_SETTINGS.get('db_default_password'),
        'HOST': SECURE_SETTINGS.get('db_default_host', '127.0.0.1'),
        'PORT': SECURE_SETTINGS.get('db_default_port', 5432),
    } 
}


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

#STATIC_URL = '/static/'
#STATIC_ROOT = '/var/wwwhtml'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'http_static/')
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]


MESSAGE_TAGS = {
            messages.SUCCESS: 'success success',
            messages.WARNING: 'warning warning',
            messages.ERROR: 'danger error'
}

PROJECT_APPS = (
    'hx_lti_initializer',
)

JENKINS_TASKS = (
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pylint',
)

CRISPY_TEMPLATE_PACK = "bootstrap3"

# Add to authentication backends (for django-auth-lti)
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_auth_lti.backends.LTIAuthBackend',
)

LTI_SETUP = {
    "TOOL_TITLE": "AnnotationsX",
    "TOOL_DESCRIPTION": "Tool for annotating texts ported from HarvardX",

    ##this is where we're getting trouble - "Resource_link_id=none" keeps showing up in the launch url.
    "LAUNCH_URL": "hx_lti_initializer:launch_lti", #"lti_init/launch_lti"
    "LAUNCH_REDIRECT_URL": "hx_lti_initializer:launch_lti",
    "INITIALIZE_MODELS": False, # Options: False|resource_only|resource_and_course|resource_and_course_users

    "EXTENSION_PARAMETERS": {
        "canvas.instructure.com": {
            "privacy_level": "public",
            "course_navigation": {
                "enabled": "true",
                "default": "enabled",
                "text": "Annotations (C9 luis)", 
            }
        }
    }
}

# Add LTI oauth credentials (for django-auth-lti)
# hard fail (keyerror) if not present
LTI_OAUTH_CREDENTIALS = SECURE_SETTINGS['lti_oauth_credentials']


#TODO: TLT SECURE
"""
Default settings for the LTI Initializer

Should set up all things needed for the Annotation tool to be set up including
the url for the tool to be accessed and for any other variables to be stored.
"""

# once in production, make sure to turn this to false
LTI_DEBUG = True

# change the url to the proper point to verify they are trying to
# access the correct location
CONSUMER_URL = 'http://54.69.120.77:8000/lti_init/launch_lti/'

# note that consumer key will be visible via the request
CONSUMER_KEY = '123key'

# the secret token will be encoded in the request.
# Only places visible are here and the secret given to the LTI consumer,
# in other words, keep it hidden!
LTI_SECRET = 'secret'

# needs context_id, collection_id, and object_id to open correct item in tool
LTI_COURSE_ID = 'context_id'
LTI_COLLECTION_ID = 'custom_collection_id'
LTI_OBJECT_ID = 'custom_object_id'

# collects roles as user needs to be an admin in order to create a profile
LTI_ROLES = 'roles'

# should be changed depending on platform roles, these are set up for edX
# TODO: Teaching assistant?
ADMIN_ROLES = {'urn:lti:instrole:ims/lis/Administrator', 'Instructor'}

X_FRAME_ALLOWED_SITES = {'tlt.harvard.edu', 'edx.org', 'canvas.harvard.edu', 'c9.io'}
X_FRAME_ALLOWED_SITES_MAP = {'tlt.harvard.edu': 'canvas.harvard.edu'}

default_app_config = 'hx_lti_initializer.apps.InitializerConfig'

ANNOTATION_DB_API_KEY = SECURE_SETTINGS.get("annotation_db_api_key")
ANNOTATION_DB_SECRET_TOKEN = SECURE_SETTINGS.get("annotation_db_secret_token")
