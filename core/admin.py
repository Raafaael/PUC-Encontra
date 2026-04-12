from django.contrib import admin
from .models import Perfil, Categoria, Local, ObjetoPerdido, ObjetoEncontrado, SolicitacaoPosse


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo', 'matricula', 'telefone')
    list_filter = ('tipo',)
    search_fields = ('user__username', 'user__first_name', 'matricula')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)


@admin.register(Local)
class LocalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'predio', 'andar')
    list_filter = ('predio',)
    search_fields = ('nome', 'predio')


@admin.register(ObjetoPerdido)
class ObjetoPerdidoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'categoria', 'local_perdido', 'data_perda', 'status')
    list_filter = ('status', 'categoria')
    search_fields = ('titulo', 'descricao')
    date_hierarchy = 'data_registro'


@admin.register(ObjetoEncontrado)
class ObjetoEncontradoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'categoria', 'local_encontrado', 'data_encontrado', 'status')
    list_filter = ('status', 'categoria')
    search_fields = ('titulo', 'descricao')
    date_hierarchy = 'data_registro'


@admin.register(SolicitacaoPosse)
class SolicitacaoPosseAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'solicitante', 'status', 'data_solicitacao')
    list_filter = ('status',)
    search_fields = ('solicitante__username', 'objeto_encontrado__titulo')
