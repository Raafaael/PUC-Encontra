from django import template

from core.permissions import get_user_tipo

register = template.Library()


@register.filter
def tipo_usuario(user):
    return get_user_tipo(user)


@register.filter
def status_class(status):
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
def query_string(request, **kwargs):
    params = request.GET.copy()
    for key, value in kwargs.items():
        if value:
            params[key] = value
        elif key in params:
            del params[key]
    return f'?{params.urlencode()}' if params else ''
