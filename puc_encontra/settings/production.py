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

hosts_permitidos_brutos = os.getenv("DJANGO_ALLOWED_HOSTS")
if not hosts_permitidos_brutos:
    raise ImproperlyConfigured(
        "Defina DJANGO_ALLOWED_HOSTS com os hosts permitidos em produção."
    )
hosts_permitidos = [
    item.strip()
    for item in hosts_permitidos_brutos.split(",")
    if item.strip()
]

origens_confiaveis_csrf_brutas = os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS")
if not origens_confiaveis_csrf_brutas:
    raise ImproperlyConfigured(
        "Defina DJANGO_CSRF_TRUSTED_ORIGINS com as origens confiáveis em produção."
    )
origens_confiaveis_csrf = [
    item.strip()
    for item in origens_confiaveis_csrf_brutas.split(",")
    if item.strip()
]

ALLOWED_HOSTS = hosts_permitidos
CSRF_TRUSTED_ORIGINS = origens_confiaveis_csrf

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
