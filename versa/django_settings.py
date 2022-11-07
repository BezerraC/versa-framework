"""
Django settings for versa-framework.

versa-framework: A framework to make discord bots

:copyright: (c) 2022 devcbezerra.
:license: Apache-2.0 OR MIT
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CWD = os.getcwd()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.getenv('PROD', False))

NAMESPACE = os.getenv('NAMESPACE', 'default')


# Application definition
INSTALLED_APPS = ['versa']
_installed = os.getenv('INSTALLED_APPS')
if _installed:
    INSTALLED_APPS += _installed.split(';')


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASE_OPTIONS = {
    'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(CWD, 'test_db.sqlite3' if DEBUG else 'db.sqlite3')
    },
    'postgres': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', None),
        'USER': os.getenv('DB_USER', None),
        'PASSWORD': os.getenv('DB_PASSWORD', None),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': int(os.getenv('DB_PORT', 5432)),
    },
    'mysql': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', None),
        'USER': os.getenv('DB_USER', None),
        'PASSWORD': os.getenv('DB_PASSWORD', None),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': int(os.getenv('DB_PORT', 3306)),
    }
}

DATABASES = {
    'default': DATABASE_OPTIONS[os.getenv('DB_TYPE', 'sqlite')]
}
