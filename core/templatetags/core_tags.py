from django import template

from core.access import obter_tipo_usuario

register = template.Library()


@register.filter
def tipo_usuario(usuario):
    return obter_tipo_usuario(usuario)


@register.filter
def classe_status(status):
    mapa = {
        'aberto': 'status-aberto',
        'encontrado': 'status-encontrado',
        'encerrado': 'status-encerrado',
        'disponivel': 'status-disponivel',
        'reivindicado': 'status-reivindicado',
        'devolvido': 'status-devolvido',
        'pendente': 'status-pendente',
        'aprovada': 'status-aprovada',
        'rejeitada': 'status-rejeitada',
    }
    return mapa.get(status, '')


@register.simple_tag
def string_consulta(requisicao, **kwargs):
    parametros = requisicao.GET.copy()
    for chave, valor in kwargs.items():
        if valor:
            parametros[chave] = valor
        elif chave in parametros:
            del parametros[chave]
    return f'?{parametros.urlencode()}' if parametros else ''
