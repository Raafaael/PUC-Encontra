from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ..access import (
    obter_tipo_usuario,
    pode_gerenciar_recurso,
    pode_ver_objeto_encontrado,
    pode_ver_objeto_perdido,
)
from ..forms import ObjetoEncontradoForm, ObjetoPerdidoForm
from ..models import ObjetoEncontrado, ObjetoPerdido


def redirecionar_erro_visibilidade(requisicao, nome_rota):
    messages.error(requisicao, 'Este item não está disponível para visualização pública.')
    return redirect(nome_rota)


@login_required
def objeto_perdido_criar(requisicao):
    perfil = getattr(requisicao.user, 'perfil', None)
    if not perfil or not perfil.telefone:
        messages.warning(requisicao, 'Preencha um telefone no seu perfil antes de registrar um item perdido.')
        return redirect('perfil')

    if requisicao.method == 'POST':
        formulario = ObjetoPerdidoForm(requisicao.POST, requisicao.FILES)
        if formulario.is_valid():
            objeto = formulario.save(commit=False)
            objeto.usuario = requisicao.user
            objeto.status = 'pendente'
            objeto.save()
            messages.success(requisicao, 'Objeto perdido registrado. Aguarde a aprovação do administrador.')
            return redirect('meus_registros')
    else:
        formulario = ObjetoPerdidoForm()

    return render(
        requisicao,
        'core/objeto_perdido_form.html',
        {'formulario': formulario, 'acao': 'Registrar'},
    )


def objeto_perdido_detalhe(requisicao, pk):
    objeto = get_object_or_404(ObjetoPerdido, pk=pk)
    tipo_usuario = obter_tipo_usuario(requisicao.user)
    pode_gerenciar_item = requisicao.user.is_authenticated and pode_gerenciar_recurso(requisicao.user, objeto.usuario)

    if not pode_ver_objeto_perdido(requisicao.user, objeto):
        return redirecionar_erro_visibilidade(requisicao, 'perdidos_publico')

    perfil_dono = getattr(objeto.usuario, 'perfil', None)
    correspondencias = []
    if objeto.categoria and objeto.status == 'aberto':
        correspondencias = ObjetoEncontrado.objects.filter(
            categoria=objeto.categoria,
            status='disponivel',
        )[:5]

    contexto = {
        'objeto': objeto,
        'correspondencias': correspondencias,
        'pode_gerenciar_item': pode_gerenciar_item,
        'pode_marcar_encontrado': pode_gerenciar_item and objeto.status == 'aberto',
        'pode_editar_ou_excluir': pode_gerenciar_item and objeto.status != 'encontrado',
        'mostrar_contato': requisicao.user.is_authenticated and requisicao.user != objeto.usuario and objeto.status == 'aberto',
        'contato_email': objeto.usuario.email,
        'contato_telefone': perfil_dono.telefone if perfil_dono and perfil_dono.telefone else '',
        'tipo': tipo_usuario,
    }
    return render(requisicao, 'core/objeto_perdido_detail.html', contexto)


@login_required
def objeto_perdido_editar(requisicao, pk):
    objeto = get_object_or_404(ObjetoPerdido, pk=pk)

    if not pode_gerenciar_recurso(requisicao.user, objeto.usuario):
        messages.error(requisicao, 'Você não tem permissão para editar este registro.')
        return redirect('meus_registros')

    if objeto.status == 'encontrado':
        messages.warning(requisicao, 'Itens marcados como encontrados não podem mais ser alterados.')
        return redirect('objeto_perdido_detail', pk=objeto.pk)

    if requisicao.method == 'POST':
        formulario = ObjetoPerdidoForm(requisicao.POST, requisicao.FILES, instance=objeto)
        if formulario.is_valid():
            formulario.save()
            messages.success(requisicao, 'Objeto perdido atualizado com sucesso.')
            return redirect('objeto_perdido_detail', pk=objeto.pk)
    else:
        formulario = ObjetoPerdidoForm(instance=objeto)

    return render(
        requisicao,
        'core/objeto_perdido_form.html',
        {'formulario': formulario, 'objeto': objeto, 'acao': 'Editar'},
    )


@login_required
def objeto_perdido_excluir(requisicao, pk):
    objeto = get_object_or_404(ObjetoPerdido, pk=pk)

    if not pode_gerenciar_recurso(requisicao.user, objeto.usuario):
        messages.error(requisicao, 'Você não tem permissão para excluir este registro.')
        return redirect('meus_registros')

    if objeto.status == 'encontrado':
        messages.warning(requisicao, 'Itens marcados como encontrados não podem mais ser excluídos.')
        return redirect('objeto_perdido_detail', pk=objeto.pk)

    if requisicao.method == 'POST':
        objeto.delete()
        messages.success(requisicao, 'Objeto perdido excluído com sucesso.')
        return redirect('meus_registros')

    return render(requisicao, 'core/confirm_delete.html', {
        'objeto': objeto,
        'tipo_nome': 'objeto perdido',
        'rota_cancelar': 'objeto_perdido_detail',
    })


@login_required
def objeto_perdido_marcar_encontrado(requisicao, pk):
    objeto = get_object_or_404(ObjetoPerdido, pk=pk)

    if not pode_gerenciar_recurso(requisicao.user, objeto.usuario):
        messages.error(requisicao, 'Você não tem permissão para alterar este registro.')
        return redirect('meus_registros')

    if requisicao.method == 'POST':
        if objeto.status == 'aberto':
            objeto.status = 'encontrado'
            objeto.save(update_fields=['status'])
            messages.success(requisicao, 'Item marcado como encontrado com sucesso.')
        else:
            messages.warning(requisicao, 'Este item não está aberto para ser marcado como encontrado.')

    return redirect('objeto_perdido_detail', pk=objeto.pk)


@login_required
def objeto_encontrado_criar(requisicao):
    if requisicao.method == 'POST':
        formulario = ObjetoEncontradoForm(requisicao.POST, requisicao.FILES)
        if formulario.is_valid():
            objeto = formulario.save(commit=False)
            objeto.usuario = requisicao.user
            objeto.status = 'pendente'
            objeto.save()
            messages.success(requisicao, 'Objeto encontrado registrado. Aguarde a aprovação do administrador.')
            return redirect('meus_registros')
    else:
        formulario = ObjetoEncontradoForm()

    return render(
        requisicao,
        'core/objeto_encontrado_form.html',
        {'formulario': formulario, 'acao': 'Registrar'},
    )


def objeto_encontrado_detalhe(requisicao, pk):
    objeto = get_object_or_404(ObjetoEncontrado, pk=pk)
    tipo_usuario = obter_tipo_usuario(requisicao.user)

    if not pode_ver_objeto_encontrado(requisicao.user, objeto):
        return redirecionar_erro_visibilidade(requisicao, 'encontrados_publico')

    correspondencias = []
    if objeto.categoria and objeto.status == 'disponivel':
        correspondencias = ObjetoPerdido.objects.filter(
            categoria=objeto.categoria,
            status='aberto',
        )[:5]

    solicitacoes = objeto.solicitacoes.select_related('solicitante').all()
    ja_solicitou = False
    minha_solicitacao = None
    if requisicao.user.is_authenticated:
        minha_solicitacao = objeto.solicitacoes.filter(solicitante=requisicao.user).first()
        ja_solicitou = minha_solicitacao is not None

    contexto = {
        'objeto': objeto,
        'correspondencias': correspondencias,
        'solicitacoes': solicitacoes,
        'ja_solicitou': ja_solicitou,
        'minha_solicitacao': minha_solicitacao,
        'tipo': tipo_usuario,
    }
    return render(requisicao, 'core/objeto_encontrado_detail.html', contexto)


@login_required
def objeto_encontrado_editar(requisicao, pk):
    objeto = get_object_or_404(ObjetoEncontrado, pk=pk)

    if not pode_gerenciar_recurso(requisicao.user, objeto.usuario):
        messages.error(requisicao, 'Você não tem permissão para editar este registro.')
        return redirect('meus_registros')

    if requisicao.method == 'POST':
        formulario = ObjetoEncontradoForm(requisicao.POST, requisicao.FILES, instance=objeto)
        if formulario.is_valid():
            formulario.save()
            messages.success(requisicao, 'Objeto encontrado atualizado com sucesso.')
            return redirect('objeto_encontrado_detail', pk=objeto.pk)
    else:
        formulario = ObjetoEncontradoForm(instance=objeto)

    return render(
        requisicao,
        'core/objeto_encontrado_form.html',
        {'formulario': formulario, 'objeto': objeto, 'acao': 'Editar'},
    )


@login_required
def objeto_encontrado_excluir(requisicao, pk):
    objeto = get_object_or_404(ObjetoEncontrado, pk=pk)

    if not pode_gerenciar_recurso(requisicao.user, objeto.usuario):
        messages.error(requisicao, 'Você não tem permissão para excluir este registro.')
        return redirect('meus_registros')

    if requisicao.method == 'POST':
        objeto.delete()
        messages.success(requisicao, 'Objeto encontrado excluído com sucesso.')
        return redirect('meus_registros')

    return render(requisicao, 'core/confirm_delete.html', {
        'objeto': objeto,
        'tipo_nome': 'objeto encontrado',
        'rota_cancelar': 'objeto_encontrado_detail',
    })
