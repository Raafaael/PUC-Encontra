from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import render

from ..access import obter_tipo_usuario
from ..models import Categoria, Objeto, SolicitacaoPosse


@login_required
def dashboard(requisicao):
    usuario = requisicao.user
    tipo = obter_tipo_usuario(usuario)
    contexto = {'tipo': tipo}

    if tipo == 'usuario':
        contexto['meus_perdidos'] = Objeto.objects.filter(usuario=usuario, tipo='perdido')[:5]
        contexto['meus_encontrados'] = Objeto.objects.filter(usuario=usuario, tipo='encontrado')[:5]
        contexto['encontrados_recentes'] = Objeto.objects.filter(tipo='encontrado', status='ativo')[:5]
        categorias_perdidas = Objeto.objects.filter(
            usuario=usuario,
            tipo='perdido',
            status='ativo',
        ).values_list('categoria_id', flat=True)
        contexto['sugestoes'] = Objeto.objects.filter(
            categoria_id__in=categorias_perdidas,
            tipo='encontrado',
            status='ativo',
        ).exclude(usuario=usuario)[:5]
    else:
        contexto['total_perdidos'] = Objeto.objects.filter(tipo='perdido').count()
        contexto['total_encontrados'] = Objeto.objects.filter(tipo='encontrado').count()
        contexto['total_devolvidos'] = Objeto.objects.filter(status='devolvido').count()
        contexto['total_usuarios'] = User.objects.count()
        contexto['pendentes_aprovacao'] = Objeto.objects.filter(status='pendente').count()
        contexto['solicitacoes_pendentes'] = SolicitacaoPosse.objects.filter(status='pendente')[:10]
        contexto['perdidos_recentes'] = Objeto.objects.filter(tipo='perdido')[:5]
        contexto['encontrados_recentes'] = Objeto.objects.filter(tipo='encontrado')[:5]
        contexto['stats_categorias'] = Categoria.objects.annotate(
            num_perdidos=Count('objetos', filter=Q(objetos__tipo='perdido')),
            num_encontrados=Count('objetos', filter=Q(objetos__tipo='encontrado')),
        ).order_by('-num_perdidos')[:5]

    return render(requisicao, 'core/dashboard.html', contexto)


@login_required
def meus_registros(requisicao):
    usuario = requisicao.user
    tipo = obter_tipo_usuario(usuario)
    filtro_tipo = requisicao.GET.get('tipo_item', '')
    filtro_status = requisicao.GET.get('status', '')

    consulta = Objeto.objects.filter(usuario=usuario)
    if filtro_tipo in ('perdido', 'encontrado'):
        consulta = consulta.filter(tipo=filtro_tipo)
    if filtro_status:
        consulta = consulta.filter(status=filtro_status)

    contexto = {
        'objetos': consulta,
        'tipo': tipo,
        'filtro_tipo': filtro_tipo,
        'filtro_status': filtro_status,
    }
    return render(requisicao, 'core/meus_registros.html', contexto)
