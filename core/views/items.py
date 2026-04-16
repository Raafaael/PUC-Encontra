from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ..access import (
    can_manage_resource,
    can_view_objeto_encontrado,
    can_view_objeto_perdido,
    get_user_tipo,
)
from ..forms import ObjetoEncontradoForm, ObjetoPerdidoForm
from ..models import ObjetoEncontrado, ObjetoPerdido


def _redirect_visibility_error(request, route_name):
    messages.error(request, 'Este item não está disponível para visualização pública.')
    return redirect(route_name)


@login_required
def objeto_perdido_create(request):
    perfil = getattr(request.user, 'perfil', None)
    if not perfil or not perfil.telefone:
        messages.warning(request, 'Preencha um telefone no seu perfil antes de registrar um item perdido.')
        return redirect('perfil')

    if request.method == 'POST':
        form = ObjetoPerdidoForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.usuario = request.user
            obj.status = 'pendente'
            obj.save()
            messages.success(request, 'Objeto perdido registrado. Aguarde a aprovação do administrador.')
            return redirect('meus_registros')
    else:
        form = ObjetoPerdidoForm()

    return render(request, 'core/objeto_perdido_form.html', {'form': form, 'acao': 'Registrar'})


def objeto_perdido_detail(request, pk):
    obj = get_object_or_404(ObjetoPerdido, pk=pk)
    tipo = get_user_tipo(request.user)
    can_manage_item = request.user.is_authenticated and can_manage_resource(request.user, obj.usuario)

    if not can_view_objeto_perdido(request.user, obj):
        return _redirect_visibility_error(request, 'perdidos_publico')

    perfil_dono = getattr(obj.usuario, 'perfil', None)
    correspondencias = []
    if obj.categoria and obj.status == 'aberto':
        correspondencias = ObjetoEncontrado.objects.filter(
            categoria=obj.categoria,
            status='disponivel',
        )[:5]

    context = {
        'obj': obj,
        'correspondencias': correspondencias,
        'can_manage_item': can_manage_item,
        'can_mark_found': can_manage_item and obj.status == 'aberto',
        'can_edit_or_delete': can_manage_item and obj.status != 'encontrado',
        'mostrar_contato': request.user.is_authenticated and request.user != obj.usuario and obj.status == 'aberto',
        'contato_email': obj.usuario.email,
        'contato_telefone': perfil_dono.telefone if perfil_dono and perfil_dono.telefone else '',
        'tipo': tipo,
    }
    return render(request, 'core/objeto_perdido_detail.html', context)


@login_required
def objeto_perdido_update(request, pk):
    obj = get_object_or_404(ObjetoPerdido, pk=pk)

    if not can_manage_resource(request.user, obj.usuario):
        messages.error(request, 'Você não tem permissão para editar este registro.')
        return redirect('meus_registros')

    if obj.status == 'encontrado':
        messages.warning(request, 'Itens marcados como encontrados nÃ£o podem mais ser alterados.')
        return redirect('objeto_perdido_detail', pk=obj.pk)

    if request.method == 'POST':
        form = ObjetoPerdidoForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Objeto perdido atualizado com sucesso.')
            return redirect('objeto_perdido_detail', pk=obj.pk)
    else:
        form = ObjetoPerdidoForm(instance=obj)

    return render(request, 'core/objeto_perdido_form.html', {'form': form, 'obj': obj, 'acao': 'Editar'})


@login_required
def objeto_perdido_delete(request, pk):
    obj = get_object_or_404(ObjetoPerdido, pk=pk)

    if not can_manage_resource(request.user, obj.usuario):
        messages.error(request, 'Você não tem permissão para excluir este registro.')
        return redirect('meus_registros')

    if obj.status == 'encontrado':
        messages.warning(request, 'Itens marcados como encontrados nÃ£o podem mais ser excluÃ­dos.')
        return redirect('objeto_perdido_detail', pk=obj.pk)

    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Objeto perdido excluído com sucesso.')
        return redirect('meus_registros')

    return render(request, 'core/confirm_delete.html', {
        'obj': obj,
        'tipo_nome': 'objeto perdido',
        'cancel_url': 'objeto_perdido_detail',
    })


@login_required
def objeto_perdido_mark_found(request, pk):
    obj = get_object_or_404(ObjetoPerdido, pk=pk)

    if not can_manage_resource(request.user, obj.usuario):
        messages.error(request, 'Você não tem permissão para alterar este registro.')
        return redirect('meus_registros')

    if request.method == 'POST':
        if obj.status == 'aberto':
            obj.status = 'encontrado'
            obj.save(update_fields=['status'])
            messages.success(request, 'Item marcado como encontrado com sucesso.')
        else:
            messages.warning(request, 'Este item não está aberto para ser marcado como encontrado.')

    return redirect('objeto_perdido_detail', pk=obj.pk)


@login_required
def objeto_encontrado_create(request):
    if request.method == 'POST':
        form = ObjetoEncontradoForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.usuario = request.user
            obj.status = 'pendente'
            obj.save()
            messages.success(request, 'Objeto encontrado registrado. Aguarde a aprovação do administrador.')
            return redirect('meus_registros')
    else:
        form = ObjetoEncontradoForm()

    return render(request, 'core/objeto_encontrado_form.html', {'form': form, 'acao': 'Registrar'})


def objeto_encontrado_detail(request, pk):
    obj = get_object_or_404(ObjetoEncontrado, pk=pk)
    tipo = get_user_tipo(request.user)

    if not can_view_objeto_encontrado(request.user, obj):
        return _redirect_visibility_error(request, 'encontrados_publico')

    correspondencias = []
    if obj.categoria and obj.status == 'disponivel':
        correspondencias = ObjetoPerdido.objects.filter(
            categoria=obj.categoria,
            status='aberto',
        )[:5]

    solicitacoes = obj.solicitacoes.select_related('solicitante').all()
    ja_solicitou = False
    minha_solicitacao = None
    if request.user.is_authenticated:
        minha_solicitacao = obj.solicitacoes.filter(solicitante=request.user).first()
        ja_solicitou = minha_solicitacao is not None

    context = {
        'obj': obj,
        'correspondencias': correspondencias,
        'solicitacoes': solicitacoes,
        'ja_solicitou': ja_solicitou,
        'minha_solicitacao': minha_solicitacao,
        'tipo': tipo,
    }
    return render(request, 'core/objeto_encontrado_detail.html', context)


@login_required
def objeto_encontrado_update(request, pk):
    obj = get_object_or_404(ObjetoEncontrado, pk=pk)

    if not can_manage_resource(request.user, obj.usuario):
        messages.error(request, 'Você não tem permissão para editar este registro.')
        return redirect('meus_registros')

    if request.method == 'POST':
        form = ObjetoEncontradoForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Objeto encontrado atualizado com sucesso.')
            return redirect('objeto_encontrado_detail', pk=obj.pk)
    else:
        form = ObjetoEncontradoForm(instance=obj)

    return render(request, 'core/objeto_encontrado_form.html', {'form': form, 'obj': obj, 'acao': 'Editar'})


@login_required
def objeto_encontrado_delete(request, pk):
    obj = get_object_or_404(ObjetoEncontrado, pk=pk)

    if not can_manage_resource(request.user, obj.usuario):
        messages.error(request, 'Você não tem permissão para excluir este registro.')
        return redirect('meus_registros')

    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Objeto encontrado excluído com sucesso.')
        return redirect('meus_registros')

    return render(request, 'core/confirm_delete.html', {
        'obj': obj,
        'tipo_nome': 'objeto encontrado',
        'cancel_url': 'objeto_encontrado_detail',
    })
