from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from ..decorators import role_required
from ..forms import AdminUsuarioForm, AprovarItemForm, CategoriaForm, LocalForm
from ..models import Categoria, Local, ObjetoEncontrado, ObjetoPerdido, Perfil, SolicitacaoPosse


@login_required
@role_required('admin')
def aprovacoes(request):
    filtro = request.GET.get('filtro', '')
    context = {'filtro': filtro}

    if filtro == 'perdidos' or not filtro:
        context['perdidos_pendentes'] = ObjetoPerdido.objects.filter(status='pendente')
    if filtro == 'encontrados' or not filtro:
        context['encontrados_pendentes'] = ObjetoEncontrado.objects.filter(status='pendente')
    if filtro == 'solicitacoes' or not filtro:
        context['solicitacoes_pendentes'] = SolicitacaoPosse.objects.filter(status='pendente')

    return render(request, 'core/aprovacoes.html', context)


@login_required
@role_required('admin')
def aprovar_item(request, tipo, pk):
    if tipo == 'perdido':
        obj = get_object_or_404(ObjetoPerdido, pk=pk)
        status_aprovado = 'aberto'
    elif tipo == 'encontrado':
        obj = get_object_or_404(ObjetoEncontrado, pk=pk)
        status_aprovado = 'disponivel'
    else:
        messages.error(request, 'Tipo inválido.')
        return redirect('aprovacoes')

    if obj.status != 'pendente':
        messages.warning(request, 'Este item já foi avaliado.')
        return redirect('aprovacoes')

    if request.method == 'POST':
        form = AprovarItemForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['acao'] == 'aprovar':
                obj.status = status_aprovado
                obj.save(update_fields=['status'])
                messages.success(request, f'Item "{obj.titulo}" aprovado e publicado.')
            else:
                obj.status = 'encerrado'
                obj.save(update_fields=['status'])
                messages.info(request, f'Item "{obj.titulo}" rejeitado.')
            return redirect('aprovacoes')
    else:
        form = AprovarItemForm()

    return render(request, 'core/aprovar_item.html', {
        'form': form,
        'obj': obj,
        'tipo': tipo,
    })


@login_required
@role_required('admin')
def categoria_list(request):
    categorias = Categoria.objects.annotate(
        num_perdidos=Count('objetos_perdidos'),
        num_encontrados=Count('objetos_encontrados'),
    )
    return render(request, 'core/categoria_list.html', {'categorias': categorias})


@login_required
@role_required('admin')
def categoria_create(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria criada com sucesso.')
            return redirect('categoria_list')
    else:
        form = CategoriaForm()

    return render(request, 'core/categoria_form.html', {'form': form, 'acao': 'Criar'})


@login_required
@role_required('admin')
def categoria_update(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso.')
            return redirect('categoria_list')
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, 'core/categoria_form.html', {
        'form': form,
        'obj': categoria,
        'acao': 'Editar',
    })


@login_required
@role_required('admin')
def categoria_delete(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoria excluída com sucesso.')
        return redirect('categoria_list')

    return render(request, 'core/confirm_delete.html', {
        'obj': categoria,
        'tipo_nome': 'categoria',
        'cancel_url_list': 'categoria_list',
    })


@login_required
@role_required('admin')
def local_list(request):
    locais = Local.objects.annotate(
        num_perdidos=Count('objetos_perdidos'),
        num_encontrados=Count('objetos_encontrados'),
    )
    return render(request, 'core/local_list.html', {'locais': locais})


@login_required
@role_required('admin')
def local_create(request):
    if request.method == 'POST':
        form = LocalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Local criado com sucesso.')
            return redirect('local_list')
    else:
        form = LocalForm()

    return render(request, 'core/local_form.html', {'form': form, 'acao': 'Criar'})


@login_required
@role_required('admin')
def local_update(request, pk):
    local = get_object_or_404(Local, pk=pk)

    if request.method == 'POST':
        form = LocalForm(request.POST, instance=local)
        if form.is_valid():
            form.save()
            messages.success(request, 'Local atualizado com sucesso.')
            return redirect('local_list')
    else:
        form = LocalForm(instance=local)

    return render(request, 'core/local_form.html', {
        'form': form,
        'obj': local,
        'acao': 'Editar',
    })


@login_required
@role_required('admin')
def local_delete(request, pk):
    local = get_object_or_404(Local, pk=pk)

    if request.method == 'POST':
        local.delete()
        messages.success(request, 'Local excluído com sucesso.')
        return redirect('local_list')

    return render(request, 'core/confirm_delete.html', {
        'obj': local,
        'tipo_nome': 'local',
        'cancel_url_list': 'local_list',
    })


@login_required
@role_required('admin')
def admin_usuarios(request):
    usuarios = User.objects.select_related('perfil').all().order_by('first_name')
    tipo_filtro = request.GET.get('tipo')
    busca = request.GET.get('q')

    if tipo_filtro:
        usuarios = usuarios.filter(perfil__tipo=tipo_filtro)
    if busca:
        usuarios = usuarios.filter(
            Q(username__icontains=busca)
            | Q(first_name__icontains=busca)
            | Q(last_name__icontains=busca)
        )

    return render(request, 'core/admin_usuarios.html', {
        'usuarios': usuarios,
        'filtro_tipo': tipo_filtro,
        'filtro_busca': busca or '',
    })


@login_required
@role_required('admin')
def admin_usuario_edit(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    perfil_obj, _ = Perfil.objects.get_or_create(
        user=usuario,
        defaults={'tipo': 'admin' if usuario.is_superuser else 'usuario'},
    )

    if request.method == 'POST':
        form = AdminUsuarioForm(request.POST, instance=perfil_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuário {usuario.username} atualizado com sucesso.')
            return redirect('admin_usuarios')
    else:
        form = AdminUsuarioForm(instance=perfil_obj)

    return render(request, 'core/admin_usuario_edit.html', {
        'form': form,
        'usuario': usuario,
    })
