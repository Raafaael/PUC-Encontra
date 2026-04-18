from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render

from ..access import obter_tipo_usuario
from ..models import Categoria, ObjetoEncontrado, ObjetoPerdido, SolicitacaoPosse


@login_required
def dashboard(requisicao):
    usuario = requisicao.user
    tipo = obter_tipo_usuario(usuario)
    contexto = {'tipo': tipo}

    if tipo == 'usuario':
        contexto['meus_perdidos'] = ObjetoPerdido.objects.filter(usuario=usuario)[:5]
        contexto['meus_encontrados'] = ObjetoEncontrado.objects.filter(usuario=usuario)[:5]
        contexto['encontrados_recentes'] = ObjetoEncontrado.objects.filter(status='disponivel')[:5]
        categorias_perdidas = ObjetoPerdido.objects.filter(
            usuario=usuario,
            status='aberto',
        ).values_list('categoria_id', flat=True)
        contexto['sugestoes'] = ObjetoEncontrado.objects.filter(
            categoria_id__in=categorias_perdidas,
            status='disponivel',
        ).exclude(usuario=usuario)[:5]
    else:
        contexto['total_perdidos'] = ObjetoPerdido.objects.count()
        contexto['total_encontrados'] = ObjetoEncontrado.objects.count()
        contexto['total_devolvidos'] = ObjetoEncontrado.objects.filter(status='devolvido').count()
        contexto['total_usuarios'] = User.objects.count()
        contexto['pendentes_aprovacao'] = (
            ObjetoPerdido.objects.filter(status='pendente').count()
            + ObjetoEncontrado.objects.filter(status='pendente').count()
        )
        contexto['solicitacoes_pendentes'] = SolicitacaoPosse.objects.filter(status='pendente')[:10]
        contexto['perdidos_recentes'] = ObjetoPerdido.objects.all()[:5]
        contexto['encontrados_recentes'] = ObjetoEncontrado.objects.all()[:5]
        contexto['stats_categorias'] = Categoria.objects.annotate(
            num_perdidos=Count('objetos_perdidos'),
            num_encontrados=Count('objetos_encontrados'),
        ).order_by('-num_perdidos')[:5]

    return render(requisicao, 'core/dashboard.html', contexto)


@login_required
def meus_registros(requisicao):
    usuario = requisicao.user
    tipo = obter_tipo_usuario(usuario)
    filtro_tipo = requisicao.GET.get('tipo_item', '')
    filtro_status = requisicao.GET.get('status', '')

    perdidos = ObjetoPerdido.objects.filter(usuario=usuario)
    encontrados = ObjetoEncontrado.objects.filter(usuario=usuario)

    if filtro_status:
        perdidos = perdidos.filter(status=filtro_status)
        encontrados = encontrados.filter(status=filtro_status)

    contexto = {
        'tipo': tipo,
        'filtro_tipo': filtro_tipo,
        'filtro_status': filtro_status,
    }

    if filtro_tipo == 'perdido':
        contexto['perdidos'] = perdidos
    elif filtro_tipo == 'encontrado':
        contexto['encontrados'] = encontrados
    else:
        contexto['perdidos'] = perdidos
        contexto['encontrados'] = encontrados

    return render(requisicao, 'core/meus_registros.html', contexto)
