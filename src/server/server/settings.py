"""
Django settings for server project.

Generated by 'django-admin startproject' using Django 2.2.13.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "foo"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "wineup.apps.WineupConfig",
    "drf_yasg",
]

logstash_host = os.environ.get("S_LOGSTASH_HOST")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "logstash": {
            "level": "INFO",
            "class": "logstash.TCPLogstashHandler",
            "host": logstash_host.split(":")[0],
            "port": int(logstash_host.split(":")[1]),
            "version": 1,
            "message_type": "django",  # 'type' field in logstash message. Default value: 'logstash'.
            "fqdn": False,
            "tags": ["ml-team-2-service"],  # list of tags. Default: None.
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "logstash"],
            "propagate": True,
        },
    },
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "server.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "server.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("S_POSTGRES_DB"),
        "USER": os.environ.get("S_POSTGRES_USER"),
        "PASSWORD": os.environ.get("S_POSTGRES_PASSWORD"),
        "HOST": os.environ.get("S_POSTGRES_HOST"),
        "PORT": os.environ.get("S_POSTGRES_PORT"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

APPEND_SLASH = False

SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "PERSIST_AUTH": True,
    "DEFAULT_MODEL_RENDERING": "example",
    "BASE_URL": os.getenv("S_BASE_URL"),
}

STATIC_URL = "/ml-team-2-service/static/"

CORS_ALLOW_ALL_ORIGINS = True

CSRF_COOKIE_SECURE = False

CSRF_COOKIE_PATH = "/ml-team-2-service/admin/"

CSRF_COOKIE_SAMESITE = False
