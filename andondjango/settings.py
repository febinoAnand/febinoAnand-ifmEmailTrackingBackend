"""
Django settings for andondjango project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path
from django.core.management.commands.runserver import Command as runserver

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY",'django-insecure-gstje5mbc3qm)j+@o@l)=kw6w3xo_2(ryf3q+q)^^ih@k)2&be')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG",True)

ALLOWED_HOSTS = ['*']
djangoHTTPPort = 9002

runserver.default_port = djangoHTTPPort
mqttServer = "localhost"
mqttPort = 1883
mqttKeepAlive = 60

httpHost = "localhost"
httpPort = djangoHTTPPort

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mqttConnection',
    'configuration',
    'devices',
    'events',
    'data',
    'emailtracking',
    'rest_framework',
    'smsgateway',
    'pushnotification',
    'corsheaders',
    'EmailTracking',
    'Userauth',
    'rest_framework.authtoken'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware'
]

REST_FRAMEWORK = {'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.AllowAny'],
                  }

CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'andondjango.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'andondjango.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

# DATETIME_FORMAT="Y-n-j\TH:i:s"

USE_I18N = True

USE_TZ = False

L10N=False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR,'static')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# # Celery Configuration Options
# CELERY_TIMEZONE = "Asia/kolkata"
# CELERY_TASK_TRACK_STARTED = True
# CELERY_TASK_TIME_LIMIT = 30 * 60
# CELERY_BROKER_URL = "redis://redis:6379"

# CELERY_TIMEZONE = os.environ.get("CELERY_TIMEZONE","Asia/kolkata")
CELERY_TASK_TRACK_STARTED = os.environ.get("CELERY_TASK_TRACK_STARTED",True)
CELERY_TASK_TIME_LIMIT = os.environ.get("CELERY_TASK_TIME_LIMIT",30 * 60)
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL","redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_BACKEND","redis://redis:6379/0")


JAZZMIN_SETTINGS={
    "site_brand": "Innospace",
}

CSRF_TRUSTED_ORIGINS = ['http://django.febinosolutions.com','https://*.127.0.0.1','http://64.227.130.181:9002/','http://innod.febinosolutions.com']


# Mobile app settings
APP_TOKEN = "ddab9b66-1a0d-4b7e-8b0c-476a0ee6cfc5"