"""Helpers para papéis de usuário e visibilidade de recursos."""

PUBLIC_PERDIDO_STATUSES = {'aberto'}
PUBLIC_ENCONTRADO_STATUSES = {'disponivel', 'reivindicado'}


def get_user_tipo(user):
    if not getattr(user, 'is_authenticated', False):
        return 'anonimo'
    if getattr(user, 'is_superuser', False):
        return 'admin'

    perfil = getattr(user, 'perfil', None)
    if perfil and perfil.tipo:
        return 'usuario' if perfil.tipo in {'aluno', 'funcionario'} else perfil.tipo
    return 'usuario'


def user_has_role(user, *roles):
    return get_user_tipo(user) in roles


def can_manage_resource(user, owner):
    return getattr(user, 'is_authenticated', False) and (
        user == owner or user_has_role(user, 'admin')
    )


def can_view_objeto_perdido(user, obj):
    return can_manage_resource(user, obj.usuario) or obj.status in PUBLIC_PERDIDO_STATUSES


def can_view_objeto_encontrado(user, obj):
    return can_manage_resource(user, obj.usuario) or obj.status in PUBLIC_ENCONTRADO_STATUSES
