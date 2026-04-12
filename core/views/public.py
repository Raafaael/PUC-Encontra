from django.db.models import Q
from django.shortcuts import redirect, render

from ..models import Categoria, Local, ObjetoEncontrado, ObjetoPerdido


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    context = {
        'total_perdidos': ObjetoPerdido.objects.filter(status='aberto').count(),
        'total_encontrados': ObjetoEncontrado.objects.filter(status='disponivel').count(),
        'total_devolvidos': ObjetoEncontrado.objects.filter(status='devolvido').count(),
    }
    return render(request, 'core/home.html', context)


def perdidos_publico(request):
    queryset = ObjetoPerdido.objects.filter(status='aberto')

    categoria_id = request.GET.get('categoria')
    local_id = request.GET.get('local')
    busca = request.GET.get('q')

    if categoria_id:
        queryset = queryset.filter(categoria_id=categoria_id)
    if local_id:
        queryset = queryset.filter(local_perdido_id=local_id)
    if busca:
        queryset = queryset.filter(Q(titulo__icontains=busca) | Q(descricao__icontains=busca))

    context = {
        'objetos': queryset,
        'categorias': Categoria.objects.all(),
        'locais': Local.objects.all(),
        'filtro_categoria': categoria_id,
        'filtro_local': local_id,
        'filtro_busca': busca or '',
        'is_public': True,
    }
    return render(request, 'core/objeto_perdido_list.html', context)


def encontrados_publico(request):
    queryset = ObjetoEncontrado.objects.filter(status__in=['disponivel', 'reivindicado'])

    categoria_id = request.GET.get('categoria')
    local_id = request.GET.get('local')
    busca = request.GET.get('q')

    if categoria_id:
        queryset = queryset.filter(categoria_id=categoria_id)
    if local_id:
        queryset = queryset.filter(local_encontrado_id=local_id)
    if busca:
        queryset = queryset.filter(Q(titulo__icontains=busca) | Q(descricao__icontains=busca))

    context = {
        'objetos': queryset,
        'categorias': Categoria.objects.all(),
        'locais': Local.objects.all(),
        'filtro_categoria': categoria_id,
        'filtro_local': local_id,
        'filtro_busca': busca or '',
        'is_public': True,
    }
    return render(request, 'core/objeto_encontrado_list.html', context)
