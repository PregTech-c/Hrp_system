from .base import *
# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
#import os
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'hrp_pregtech',                      # Or path to database file if using sqlite3.
        'USER': 'pregtech',                      # Not used with sqlite3.
       	'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    },
    'sqllite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
#EMAIL_HOST='smtp.gmail.com'
#EMAIL_PORT='587'
#EMAIL_HOST_USER='ernstyoung2017@gmail.com' #'regina.kimera@gmail.com'
#EMAIL_USE_TLS=True
#EMAIL_HOST_PASSWORD='ernst2016' #'ernstandyoung'
#EMAIL_SUBJECT_PREFIX='[Payroll]'
#EMAIL_FROM_ADDRESS='ernstyoung2017@gmail.com' #'regina.kimera@gmail.com'

HRP = {
    'HRP_SHORT_DATE_FORMAT': 'd/m/Y',
    'COMPANY': {
        'NAME': 'Preg-tech Uganda Ltd',
        'ADDRESS': 'Plot 18 Clement Hill Road',
        'TELEPHONE': '+25641-4343520/4'
    },
    'TABLE_PAGINATOR_CONF': {'body': 10, 'padding': 1, 'tail': 5, 'padding': 2}, 
}

SESSION_EXPIRE_AT_BROWSER_CLOSE=True
SESSION_SECURITY_WARN_AFTER=180
SESSION_SECURITY_EXPIRE_AFTER=300

EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT='587'
EMAIL_HOST_USER='hrp.sys.demo@gmail.com'
EMAIL_USE_TLS=True
EMAIL_HOST_PASSWORD='PTC1102re.'
EMAIL_SUBJECT_PREFIX='[Payroll]'
EMAIL_FROM_ADDRESS='hrp.sys.demo@gmail.com'

