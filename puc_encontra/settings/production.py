import os

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from .base import *

DEBUG = False

if SECRET_KEY.startswith("django-insecure-"):
    raise ImproperlyConfigured(
        "Defina DJANGO_SECRET_KEY com um valor seguro para produção."
    )

url_banco_dados = os.getenv("DATABASE_URL")
if not url_banco_dados:
    raise ImproperlyConfigured(
        "Defina DATABASE_URL para conectar o banco de dados em produção."
    )

dominio_publico_railway = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()

hosts_permitidos = set(ambiente_lista("DJANGO_ALLOWED_HOSTS"))
if dominio_publico_railway:
    hosts_permitidos.add(dominio_publico_railway)
if not hosts_permitidos:
    raise ImproperlyConfigured(
        "Defina DJANGO_ALLOWED_HOSTS com o domínio do Railway e/ou domínio customizado."
    )
ALLOWED_HOSTS = sorted(hosts_permitidos)

origens_confiaveis_csrf = set(ambiente_lista("DJANGO_CSRF_TRUSTED_ORIGINS"))
if dominio_publico_railway:
    origens_confiaveis_csrf.add(f"https://{dominio_publico_railway}")
CSRF_TRUSTED_ORIGINS = sorted(origens_confiaveis_csrf)

DATABASES = {
    "default": dj_database_url.parse(
        url_banco_dados,
        conn_max_age=600,
        ssl_require=ambiente_booleano("DJANGO_DB_SSL_REQUIRE", True),
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
SECURE_SSL_REDIRECT = ambiente_booleano("DJANGO_SECURE_SSL_REDIRECT", True)
SESSION_COOKIE_SECURE = ambiente_booleano("DJANGO_SESSION_COOKIE_SECURE", True)
CSRF_COOKIE_SECURE = ambiente_booleano("DJANGO_CSRF_COOKIE_SECURE", True)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = os.getenv("DJANGO_SECURE_REFERRER_POLICY", "same-origin")
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "3600"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = ambiente_booleano(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", False
)
SECURE_HSTS_PRELOAD = ambiente_booleano("DJANGO_SECURE_HSTS_PRELOAD", False)

SERVE_MEDIA_FILES = ambiente_booleano("DJANGO_SERVE_MEDIA_FILES", True)
