import os

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from .base import *

DEBUG = False

if SECRET_KEY.startswith("django-insecure-"):
    raise ImproperlyConfigured(
        "Defina DJANGO_SECRET_KEY com um valor seguro para produção."
    )

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ImproperlyConfigured(
        "Defina DATABASE_URL para conectar o banco de dados em produção."
    )

railway_public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()

allowed_hosts = set(env_list("DJANGO_ALLOWED_HOSTS"))
if railway_public_domain:
    allowed_hosts.add(railway_public_domain)
if not allowed_hosts:
    raise ImproperlyConfigured(
        "Defina DJANGO_ALLOWED_HOSTS com o domínio do Railway e/ou domínio customizado."
    )
ALLOWED_HOSTS = sorted(allowed_hosts)

csrf_trusted_origins = set(env_list("DJANGO_CSRF_TRUSTED_ORIGINS"))
if railway_public_domain:
    csrf_trusted_origins.add(f"https://{railway_public_domain}")
CSRF_TRUSTED_ORIGINS = sorted(csrf_trusted_origins)

DATABASES = {
    "default": dj_database_url.parse(
        database_url,
        conn_max_age=600,
        ssl_require=env_bool("DJANGO_DB_SSL_REQUIRE", True),
    )
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE[1:],
]

STORAGES = {
    **STORAGES,
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", True)
CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", True)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = os.getenv("DJANGO_SECURE_REFERRER_POLICY", "same-origin")
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "3600"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", False
)
SECURE_HSTS_PRELOAD = env_bool("DJANGO_SECURE_HSTS_PRELOAD", False)

SERVE_MEDIA_FILES = env_bool("DJANGO_SERVE_MEDIA_FILES", True)
