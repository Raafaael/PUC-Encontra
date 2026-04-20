from django.db.models import Q
from django.shortcuts import redirect, render

from ..models import Categoria, Local, Objeto


def home(requisicao):
    if requisicao.user.is_authenticated:
        return redirect('dashboard')

    contexto = {
        'total_perdidos': Objeto.objects.filter(tipo='perdido', status='ativo').count(),
        'total_encontrados': Objeto.objects.filter(tipo='encontrado', status='ativo').count(),
        'total_devolvidos': Objeto.objects.filter(status='devolvido').count(),
    }
    return render(requisicao, 'core/home.html', contexto)


def itens_publico(requisicao):
    filtro_tipo = requisicao.GET.get('tipo', '')
    categoria_id = requisicao.GET.get('categoria')
    local_id = requisicao.GET.get('local')
    busca = requisicao.GET.get('q')

    if filtro_tipo == 'devolvido':
        consulta = Objeto.objects.filter(status='devolvido')
    elif filtro_tipo in ('perdido', 'encontrado'):
        consulta = Objeto.objects.filter(tipo=filtro_tipo, status='ativo')
    else:
        consulta = Objeto.objects.filter(status='ativo')

    if categoria_id:
        consulta = consulta.filter(categoria_id=categoria_id)
    if local_id:
        consulta = consulta.filter(local_id=local_id)
    if busca:
        consulta = consulta.filter(Q(titulo__icontains=busca) | Q(descricao__icontains=busca))

    contexto = {
        'objetos': consulta,
        'categorias': Categoria.objects.all(),
        'locais': Local.objects.all(),
        'filtro_tipo': filtro_tipo,
        'filtro_categoria': categoria_id,
        'filtro_local': local_id,
        'filtro_busca': busca or '',
    }
    return render(requisicao, 'core/objeto_list.html', contexto)
