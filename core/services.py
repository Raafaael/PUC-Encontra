"""Regras de negócio compartilhadas entre views e formulários."""

from .models import Objeto, SolicitacaoEdicao


def cancelar_solicitacoes_pendentes_usuario(usuario):
    """Remove pendências abertas do usuário ao desativar a conta."""

    registros_pendentes = Objeto.objects.filter(usuario=usuario, status='pendente')
    total_registros_pendentes = registros_pendentes.count()
    registros_pendentes.delete()

    total_edicoes_pendentes = SolicitacaoEdicao.objects.filter(
        solicitante=usuario,
        status='pendente',
    ).update(status='rejeitada')

    return {
        'registros_pendentes_cancelados': total_registros_pendentes,
        'edicoes_pendentes_canceladas': total_edicoes_pendentes,
    }
