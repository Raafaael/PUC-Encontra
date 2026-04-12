"""
Configuração de URLs do projeto PUC Encontra.

Inclui as URLs da aplicação core e serve arquivos de mídia em modo debug.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),  # Admin nativo do Django
    path('', include('core.urls')),           # URLs da aplicação principal
]

# Servir arquivos de mídia em modo de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
