from distutils.version import StrictVersion
from os import path

import django

DJANGO_VERSION = StrictVersion(django.get_version())

DEBUG = True
TEMPLATE_DEBUG = True
USE_TZ = True
USE_L10N = True

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "example.db"},
}

ALLOWED_HOSTS = ["localhost", ".ngrok.io"]

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

DJANGO_ATLASSIAN_VENDOR_NAME = "Fluendo S.A."
DJANGO_ATLASSIAN_VENDOR_URL = "https://fluendo.com"

DJANGO_ATLASSIAN_CONFLUENCE_NAME = "Hello World"
DJANGO_ATLASSIAN_CONFLUENCE_DESCRIPTION = (
    "Sample application based on django-atlassian-connect"
)
DJANGO_ATLASSIAN_CONFLUENCE_KEY = "fluendo-example"
DJANGO_ATLASSIAN_CONFLUENCE_SCOPES = ["read"]

DJANGO_ATLASSIAN_JIRA_NAME = "Hello World"
DJANGO_ATLASSIAN_JIRA_DESCRIPTION = (
    "Sample application based on django-atlassian-connect"
)
DJANGO_ATLASSIAN_JIRA_KEY = "fluendo-example"
DJANGO_ATLASSIAN_JIRA_SCOPES = ["read"]
DJANGO_ATLASSIAN_LICENSING = False

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_atlassian_connect",
    "example.helloworld",
)

MIDDLEWARE = [
    # default django middleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

PROJECT_DIR = path.abspath(path.join(path.dirname(__file__)))

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [path.join(PROJECT_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.messages.context_processors.messages",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.request",
            ]
        },
    }
]

STATIC_URL = "/static/"

SECRET_KEY = "secret"  # noqa: S105

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "%(levelname)s %(message)s"}},
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        }
    },
    "loggers": {
        "": {"handlers": ["console"], "propagate": True, "level": "DEBUG"},
    },
}

ROOT_URLCONF = "example.urls"

if not DEBUG:
    raise Exception("This settings file can only be used with DEBUG=True")
