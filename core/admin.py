from django.contrib import admin

from .models import *

admin.site.register([
    Perfil,
    Categoria,
    Local,
    Objeto,
    SolicitacaoEdicao,
    CodigoVerificacao,
])
