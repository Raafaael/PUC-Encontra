import os

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from .base import *

DEBUG = False

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    raise ImproperlyConfigured(
        "Defina DJANGO_SECRET_KEY com um valor seguro para produção."
    )


url_banco_dados = os.getenv("DATABASE_URL")
if not url_banco_dados:
    raise ImproperlyConfigured(
        "Defina DATABASE_URL para conectar o banco de dados em produção."
    )

dominio_publico_railway = os.getenv("RAILWAY_PUBLIC_DOMAIN")
if not dominio_publico_railway:
    raise ImproperlyConfigured(
        "Defina RAILWAY_PUBLIC_DOMAIN com o domínio público da aplicação."
    )

ALLOWED_HOSTS = [dominio_publico_railway]
CSRF_TRUSTED_ORIGINS = [f"https://{dominio_publico_railway}"]

DATABASES = {
    "default": dj_database_url.parse(
        url_banco_dados,
        conn_max_age=600,
        ssl_require=True,
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

STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = Path("/data/media")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SERVE_MEDIA_FILES = True
REGISTRO_EXIGE_VERIFICACAO_EMAIL = False
