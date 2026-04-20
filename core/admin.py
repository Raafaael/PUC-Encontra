from django.contrib import admin
from .models import Perfil, Categoria, Local, Objeto


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


@admin.register(Objeto)
class ObjetoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'usuario', 'categoria', 'local', 'data_ocorrencia', 'status')
    list_filter = ('tipo', 'status', 'categoria')
    search_fields = ('titulo', 'descricao')
    date_hierarchy = 'data_registro'
