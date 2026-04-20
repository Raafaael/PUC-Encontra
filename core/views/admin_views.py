from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from ..decorators import papel_obrigatorio
from ..forms import AdminCreateForm, AdminUsuarioForm, AprovarItemForm, CategoriaForm, LocalForm
from ..models import Categoria, Local, Objeto, Perfil, SolicitacaoPosse


@login_required
@papel_obrigatorio('admin')
def aprovacoes(requisicao):
    filtro = requisicao.GET.get('filtro', '')
    contexto = {'filtro': filtro}

    if filtro == 'perdidos' or not filtro:
        contexto['perdidos_pendentes'] = Objeto.objects.filter(tipo='perdido', status='pendente')
    if filtro == 'encontrados' or not filtro:
        contexto['encontrados_pendentes'] = Objeto.objects.filter(tipo='encontrado', status='pendente')
    if filtro == 'solicitacoes' or not filtro:
        contexto['solicitacoes_pendentes'] = SolicitacaoPosse.objects.filter(status='pendente')

    return render(requisicao, 'core/aprovacoes.html', contexto)


@login_required
@papel_obrigatorio('admin')
def aprovar_item(requisicao, pk):
    objeto = get_object_or_404(Objeto, pk=pk)

    if objeto.status != 'pendente':
        messages.warning(requisicao, 'Este item já foi avaliado.')
        return redirect('aprovacoes')

    if requisicao.method == 'POST':
        formulario = AprovarItemForm(requisicao.POST)
        if formulario.is_valid():
            if formulario.cleaned_data['acao'] == 'aprovar':
                objeto.status = 'ativo'
                objeto.save(update_fields=['status'])
                messages.success(requisicao, f'Item "{objeto.titulo}" aprovado e publicado.')
            else:
                titulo = objeto.titulo
                objeto.delete()
                messages.info(requisicao, f'Item "{titulo}" rejeitado e removido.')
            return redirect('aprovacoes')
    else:
        formulario = AprovarItemForm()

    return render(requisicao, 'core/aprovar_item.html', {
        'formulario': formulario,
        'objeto': objeto,
    })


@login_required
@papel_obrigatorio('admin')
def categoria_listar(requisicao):
    categorias = Categoria.objects.annotate(
        num_perdidos=Count('objetos', filter=Q(objetos__tipo='perdido')),
        num_encontrados=Count('objetos', filter=Q(objetos__tipo='encontrado')),
    )
    return render(requisicao, 'core/categoria_list.html', {'categorias': categorias})


@login_required
@papel_obrigatorio('admin')
def categoria_criar(requisicao):
    if requisicao.method == 'POST':
        formulario = CategoriaForm(requisicao.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(requisicao, 'Categoria criada com sucesso.')
            return redirect('categoria_list')
    else:
        formulario = CategoriaForm()

    return render(
        requisicao,
        'core/categoria_form.html',
        {'formulario': formulario, 'acao': 'Criar'},
    )


@login_required
@papel_obrigatorio('admin')
def categoria_editar(requisicao, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    if requisicao.method == 'POST':
        formulario = CategoriaForm(requisicao.POST, instance=categoria)
        if formulario.is_valid():
            formulario.save()
            messages.success(requisicao, 'Categoria atualizada com sucesso.')
            return redirect('categoria_list')
    else:
        formulario = CategoriaForm(instance=categoria)

    return render(requisicao, 'core/categoria_form.html', {
        'formulario': formulario,
        'objeto': categoria,
        'acao': 'Editar',
    })


@login_required
@papel_obrigatorio('admin')
def categoria_excluir(requisicao, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    if requisicao.method == 'POST':
        categoria.delete()
        messages.success(requisicao, 'Categoria excluída com sucesso.')
        return redirect('categoria_list')

    return render(requisicao, 'core/confirm_delete.html', {
        'objeto': categoria,
        'tipo_nome': 'categoria',
        'rota_cancelar_lista': 'categoria_list',
    })


@login_required
@papel_obrigatorio('admin')
def local_listar(requisicao):
    locais = Local.objects.annotate(
        num_perdidos=Count('objetos', filter=Q(objetos__tipo='perdido')),
        num_encontrados=Count('objetos', filter=Q(objetos__tipo='encontrado')),
    )
    return render(requisicao, 'core/local_list.html', {'locais': locais})


@login_required
@papel_obrigatorio('admin')
def local_criar(requisicao):
    if requisicao.method == 'POST':
        formulario = LocalForm(requisicao.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(requisicao, 'Local criado com sucesso.')
            return redirect('local_list')
    else:
        formulario = LocalForm()

    return render(
        requisicao,
        'core/local_form.html',
        {'formulario': formulario, 'acao': 'Criar'},
    )


@login_required
@papel_obrigatorio('admin')
def local_editar(requisicao, pk):
    local = get_object_or_404(Local, pk=pk)

    if requisicao.method == 'POST':
        formulario = LocalForm(requisicao.POST, instance=local)
        if formulario.is_valid():
            formulario.save()
            messages.success(requisicao, 'Local atualizado com sucesso.')
            return redirect('local_list')
    else:
        formulario = LocalForm(instance=local)

    return render(requisicao, 'core/local_form.html', {
        'formulario': formulario,
        'objeto': local,
        'acao': 'Editar',
    })


@login_required
@papel_obrigatorio('admin')
def local_excluir(requisicao, pk):
    local = get_object_or_404(Local, pk=pk)

    if requisicao.method == 'POST':
        local.delete()
        messages.success(requisicao, 'Local excluído com sucesso.')
        return redirect('local_list')

    return render(requisicao, 'core/confirm_delete.html', {
        'objeto': local,
        'tipo_nome': 'local',
        'rota_cancelar_lista': 'local_list',
    })


@login_required
@papel_obrigatorio('admin')
def listar_usuarios_admin(requisicao):
    usuarios = User.objects.select_related('perfil').all().order_by('first_name')
    tipo_filtro = requisicao.GET.get('tipo')
    busca = requisicao.GET.get('q')

    if tipo_filtro:
        usuarios = usuarios.filter(perfil__tipo=tipo_filtro)
    if busca:
        usuarios = usuarios.filter(
            Q(username__icontains=busca)
            | Q(first_name__icontains=busca)
            | Q(last_name__icontains=busca)
        )

    return render(requisicao, 'core/admin_usuarios.html', {
        'usuarios': usuarios,
        'filtro_tipo': tipo_filtro,
        'filtro_busca': busca or '',
    })


@login_required
@papel_obrigatorio('admin')
def criar_usuario_admin(requisicao):
    if requisicao.method == 'POST':
        formulario = AdminCreateForm(requisicao.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            messages.success(
                requisicao,
                f'Administrador {usuario.username} criado com sucesso.',
            )
            return redirect('admin_usuarios')
    else:
        formulario = AdminCreateForm()

    return render(requisicao, 'core/admin_usuario_create.html', {'formulario': formulario})


@login_required
@papel_obrigatorio('admin')
def editar_usuario_admin(requisicao, pk):
    usuario = get_object_or_404(User, pk=pk)
    perfil_usuario = Perfil.objects.get_or_create(
        user=usuario,
        defaults={'tipo': 'admin' if usuario.is_superuser else 'usuario'},
    )[0]

    if requisicao.method == 'POST':
        formulario = AdminUsuarioForm(requisicao.POST, instance=perfil_usuario)
        if formulario.is_valid():
            formulario.save()
            messages.success(requisicao, f'Usuário {usuario.username} atualizado com sucesso.')
            return redirect('admin_usuarios')
    else:
        formulario = AdminUsuarioForm(instance=perfil_usuario)

    return render(requisicao, 'core/admin_usuario_edit.html', {
        'formulario': formulario,
        'usuario': usuario,
    })
