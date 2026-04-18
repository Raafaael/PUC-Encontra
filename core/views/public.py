from django.db.models import Q
from django.shortcuts import redirect, render

from ..models import Categoria, Local, ObjetoEncontrado, ObjetoPerdido


def home(requisicao):
    if requisicao.user.is_authenticated:
        return redirect('dashboard')

    contexto = {
        'total_perdidos': ObjetoPerdido.objects.filter(status='aberto').count(),
        'total_encontrados': ObjetoEncontrado.objects.filter(status='disponivel').count(),
        'total_devolvidos': ObjetoEncontrado.objects.filter(status='devolvido').count(),
    }
    return render(requisicao, 'core/home.html', contexto)


def perdidos_publico(requisicao):
    consulta = ObjetoPerdido.objects.filter(status='aberto')

    categoria_id = requisicao.GET.get('categoria')
    local_id = requisicao.GET.get('local')
    busca = requisicao.GET.get('q')

    if categoria_id:
        consulta = consulta.filter(categoria_id=categoria_id)
    if local_id:
        consulta = consulta.filter(local_perdido_id=local_id)
    if busca:
        consulta = consulta.filter(Q(titulo__icontains=busca) | Q(descricao__icontains=busca))

    contexto = {
        'objetos': consulta,
        'categorias': Categoria.objects.all(),
        'locais': Local.objects.all(),
        'filtro_categoria': categoria_id,
        'filtro_local': local_id,
        'filtro_busca': busca or '',
        'eh_publico': True,
    }
    return render(requisicao, 'core/objeto_perdido_list.html', contexto)


def encontrados_publico(requisicao):
    consulta = ObjetoEncontrado.objects.filter(status__in=['disponivel', 'reivindicado'])

    categoria_id = requisicao.GET.get('categoria')
    local_id = requisicao.GET.get('local')
    busca = requisicao.GET.get('q')

    if categoria_id:
        consulta = consulta.filter(categoria_id=categoria_id)
    if local_id:
        consulta = consulta.filter(local_encontrado_id=local_id)
    if busca:
        consulta = consulta.filter(Q(titulo__icontains=busca) | Q(descricao__icontains=busca))

    contexto = {
        'objetos': consulta,
        'categorias': Categoria.objects.all(),
        'locais': Local.objects.all(),
        'filtro_categoria': categoria_id,
        'filtro_local': local_id,
        'filtro_busca': busca or '',
        'eh_publico': True,
    }
    return render(requisicao, 'core/objeto_encontrado_list.html', contexto)
