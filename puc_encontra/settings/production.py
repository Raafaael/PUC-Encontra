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

dominio_publico_vercel = os.getenv("HOST_PUBLIC_DOMAIN")
if not dominio_publico_vercel:
    raise ImproperlyConfigured(
        "Defina HOST_PUBLIC_DOMAIN com o domínio público da aplicação."
    )

ALLOWED_HOSTS = [dominio_publico_vercel]
CSRF_TRUSTED_ORIGINS = [f"https://{dominio_publico_vercel}"]

DATABASES = {
    "default": dj_database_url.parse(
        url_banco_dados,
        conn_max_age=600,
        ssl_require=True,
    )
}

INSTALLED_APPS += ["cloudinary_storage", "cloudinary"]

cloudinary_cloud_name = os.getenv("CLOUD_NAME")
cloudinary_api_key = os.getenv("CLOUD_API_KEY")
cloudinary_api_secret = os.getenv("CLOUD_API_SECRET")

if not cloudinary_api_key or not cloudinary_api_secret:
    raise ImproperlyConfigured(
        "Defina CLOUD_API_KEY/CLOUD_API_SECRET ou CLOUDINARY_API_KEY/CLOUDINARY_API_SECRET para o Cloudinary."
    )

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": cloudinary_cloud_name,
    "API_KEY": cloudinary_api_key,
    "API_SECRET": cloudinary_api_secret,
    "PREFIX": "puc_encontra",
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE[1:],
]

STORAGES = {
    **STORAGES,
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
}


STATIC_ROOT = BASE_DIR / "staticfiles"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SERVE_MEDIA_FILES = False
REGISTRO_EXIGE_VERIFICACAO_EMAIL = False
