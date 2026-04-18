from .base import *


DEBUG = True

ALLOWED_HOSTS = ambiente_lista("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = ambiente_lista(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000",
)

SERVE_MEDIA_FILES = True
