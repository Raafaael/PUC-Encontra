"""
Configuração WSGI para o projeto PUC Encontra.

Expõe o callable WSGI como variável de módulo chamada 'application'.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puc_encontra.settings')
application = get_wsgi_application()
