"""Permissões e papéis de usuário para controle de acesso e visibilidade."""

STATUS_PUBLICOS_PERDIDO = {'aberto'}
STATUS_PUBLICOS_ENCONTRADO = {'disponivel', 'reivindicado'}


def obter_tipo_usuario(usuario):
    if not getattr(usuario, 'is_authenticated', False):
        return 'anonimo'
    if getattr(usuario, 'is_superuser', False):
        return 'admin'

    perfil = getattr(usuario, 'perfil', None)
    if perfil and perfil.tipo:
        return perfil.tipo
    return 'usuario'


def usuario_tem_papel(usuario, *papeis):
    return obter_tipo_usuario(usuario) in papeis


def pode_gerenciar_recurso(usuario, dono):
    return getattr(usuario, 'is_authenticated', False) and (
        usuario == dono or usuario_tem_papel(usuario, 'admin')
    )


def pode_ver_objeto_perdido(usuario, objeto):
    return pode_gerenciar_recurso(usuario, objeto.usuario) or objeto.status in STATUS_PUBLICOS_PERDIDO


def pode_ver_objeto_encontrado(usuario, objeto):
    return pode_gerenciar_recurso(usuario, objeto.usuario) or objeto.status in STATUS_PUBLICOS_ENCONTRADO
