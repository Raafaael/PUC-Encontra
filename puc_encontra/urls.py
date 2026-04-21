"""
Configuração de URLs do projeto PUC Encontra.
"""

import re

from django.contrib import admin
from django.conf import settings
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),  # Admin nativo do Django
    path("", include("core.urls")),  # URLs da aplicação principal
]

if getattr(settings, "SERVE_MEDIA_FILES", False):
    media_prefix = settings.MEDIA_URL.lstrip("/")
    if media_prefix and not media_prefix.endswith("/"):
        media_prefix = f"{media_prefix}/"
    urlpatterns += [
        re_path(
            rf"^{re.escape(media_prefix)}(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        )
    ]
