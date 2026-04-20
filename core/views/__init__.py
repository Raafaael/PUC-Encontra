from .account import desativar_conta, perfil, registro, trocar_senha, verificar_email
from .admin_views import (
    criar_usuario_admin,
    editar_usuario_admin,
    listar_usuarios_admin,
    aprovacoes,
    aprovar_item,
    categoria_criar,
    categoria_excluir,
    categoria_listar,
    categoria_editar,
    local_criar,
    local_excluir,
    local_listar,
    local_editar,
)
from .claims import solicitacao_criar, solicitacao_detalhe, solicitacao_avaliar
from .dashboard import dashboard, meus_registros
from .items import objeto_criar, objeto_detalhe, objeto_editar, objeto_excluir, objeto_marcar_devolvido
from .public import home, itens_publico

__all__ = [
    'aprovacoes',
    'aprovar_item',
    'categoria_criar',
    'categoria_excluir',
    'categoria_listar',
    'categoria_editar',
    'criar_usuario_admin',
    'dashboard',
    'desativar_conta',
    'editar_usuario_admin',
    'home',
    'itens_publico',
    'listar_usuarios_admin',
    'local_criar',
    'local_excluir',
    'local_listar',
    'local_editar',
    'meus_registros',
    'objeto_criar',
    'objeto_detalhe',
    'objeto_editar',
    'objeto_excluir',
    'perfil',
    'registro',
    'solicitacao_avaliar',
    'solicitacao_criar',
    'solicitacao_detalhe',
    'trocar_senha',
    'verificar_email',
]
