import dj_database_url
import django
from django.utils.encoding import force_str

from .base import *

django.utils.encoding.force_text = force_str


DEBUG = os.environ.get("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]

RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    "default": dj_database_url.config(
        conn_max_age=500,
        conn_health_checks=True,
    ),
}

# Security
SECURE_SSL_REDIRECT = os.environ.get("DJANGO_SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60
