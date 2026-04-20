"""Helpers para papéis de usuário e visibilidade de recursos."""

STATUS_PUBLICOS = {'ativo', 'reivindicado', 'devolvido'}


def obter_tipo_usuario(usuario):
    if not getattr(usuario, 'is_authenticated', False):
        return 'anonimo'
    if getattr(usuario, 'is_superuser', False):
        return 'admin'

    perfil = getattr(usuario, 'perfil', None)
    if perfil and perfil.tipo:
        return 'usuario' if perfil.tipo in {'aluno', 'funcionario'} else perfil.tipo
    return 'usuario'


def usuario_tem_papel(usuario, *papeis):
    return obter_tipo_usuario(usuario) in papeis


def pode_gerenciar_recurso(usuario, dono):
    return getattr(usuario, 'is_authenticated', False) and (
        usuario == dono or usuario_tem_papel(usuario, 'admin')
    )


def pode_ver_objeto(usuario, objeto):
    return pode_gerenciar_recurso(usuario, objeto.usuario) or objeto.status in STATUS_PUBLICOS
