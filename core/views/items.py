from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ..access import obter_tipo_usuario, pode_gerenciar_recurso, pode_ver_objeto
from ..decorators import papel_obrigatorio
from ..forms import EdicaoForm, ObjetoForm
from ..models import Objeto, SolicitacaoEdicao


def redirecionar_erro_visibilidade(requisicao):
    messages.error(requisicao, 'Este item não está disponível para visualização pública.')
    return redirect('itens_publico')


@login_required
def objeto_criar(requisicao):
    eh_admin = obter_tipo_usuario(requisicao.user) == 'admin'

    if requisicao.method == 'POST':
        formulario = ObjetoForm(requisicao.POST, requisicao.FILES)
        if formulario.is_valid():
            tipo = formulario.cleaned_data['tipo']

            if tipo == 'perdido' and not eh_admin:
                perfil = getattr(requisicao.user, 'perfil', None)
                if not perfil or not perfil.telefone:
                    messages.warning(requisicao, 'Preencha um telefone no seu perfil antes de registrar um item perdido.')
                    return redirect('perfil')

            objeto = formulario.save(commit=False)
            objeto.usuario = requisicao.user
            objeto.status = 'ativo' if eh_admin else 'pendente'
            objeto.save()
            if eh_admin:
                messages.success(requisicao, 'Item registrado e publicado.')
            else:
                messages.success(requisicao, 'Item registrado. Aguarde a aprovação do administrador.')
            return redirect('meus_registros')
    else:
        formulario = ObjetoForm()

    return render(requisicao, 'core/objeto_form.html', {
        'formulario': formulario,
        'acao': 'Registrar',
    })


def objeto_detalhe(requisicao, pk):
    objeto = get_object_or_404(Objeto, pk=pk)
    tipo_usuario = obter_tipo_usuario(requisicao.user)
    pode_gerenciar_item = requisicao.user.is_authenticated and pode_gerenciar_recurso(requisicao.user, objeto.usuario)

    if not pode_ver_objeto(requisicao.user, objeto):
        return redirecionar_erro_visibilidade(requisicao)

    correspondencias = []
    if objeto.categoria and objeto.status == 'ativo':
        tipo_correspondencia = 'encontrado' if objeto.tipo == 'perdido' else 'perdido'
        correspondencias = Objeto.objects.filter(
            categoria=objeto.categoria,
            tipo=tipo_correspondencia,
            status='ativo',
        ).exclude(pk=objeto.pk)[:5]

    perfil_dono = getattr(objeto.usuario, 'perfil', None)
    mostrar_contato = (
        requisicao.user.is_authenticated
        and requisicao.user != objeto.usuario
        and objeto.status == 'ativo'
    )

    contexto = {
        'objeto': objeto,
        'correspondencias': correspondencias,
        'pode_gerenciar_item': pode_gerenciar_item,
        'pode_editar_ou_excluir': pode_gerenciar_item and objeto.status != 'devolvido',
        'mostrar_contato': mostrar_contato,
        'contato_email': objeto.usuario.email,
        'contato_telefone': perfil_dono.telefone if perfil_dono and perfil_dono.telefone else '',
        'tipo': tipo_usuario,
    }
    return render(requisicao, 'core/objeto_detail.html', contexto)


@login_required
def objeto_editar(requisicao, pk):
    objeto = get_object_or_404(Objeto, pk=pk)
    eh_admin = obter_tipo_usuario(requisicao.user) == 'admin'

    if not pode_gerenciar_recurso(requisicao.user, objeto.usuario):
        messages.error(requisicao, 'Você não tem permissão para editar este registro.')
        return redirect('meus_registros')

    if objeto.status == 'devolvido':
        messages.warning(requisicao, 'Este item não pode mais ser alterado.')
        return redirect('objeto_detail', pk=objeto.pk)

    if not eh_admin and SolicitacaoEdicao.objects.filter(objeto=objeto, status='pendente').exists():
        messages.warning(requisicao, 'Você já tem uma edição aguardando aprovação para este item.')
        return redirect('objeto_detail', pk=objeto.pk)

    if eh_admin:
        if requisicao.method == 'POST':
            formulario = ObjetoForm(requisicao.POST, requisicao.FILES, instance=objeto)
            if formulario.is_valid():
                formulario.save()
                messages.success(requisicao, 'Item atualizado com sucesso.')
                return redirect('objeto_detail', pk=objeto.pk)
        else:
            formulario = ObjetoForm(instance=objeto)
        return render(requisicao, 'core/objeto_form.html', {
            'formulario': formulario,
            'objeto': objeto,
            'acao': 'Editar',
        })

    # Usuário comum — cria solicitação de edição
    edicao_inicial = {
        'titulo': objeto.titulo,
        'descricao': objeto.descricao,
        'categoria': objeto.categoria,
        'local': objeto.local,
        'data_ocorrencia': objeto.data_ocorrencia,
    }
    if requisicao.method == 'POST':
        formulario = EdicaoForm(requisicao.POST, requisicao.FILES)
        if formulario.is_valid():
            SolicitacaoEdicao.objects.filter(objeto=objeto).exclude(status='pendente').delete()
            edicao = formulario.save(commit=False)
            edicao.objeto = objeto
            edicao.solicitante = requisicao.user
            edicao.save()
            messages.success(requisicao, 'Solicitação de edição enviada. Aguarde a aprovação do administrador.')
            return redirect('objeto_detail', pk=objeto.pk)
    else:
        formulario = EdicaoForm(initial=edicao_inicial)

    return render(requisicao, 'core/objeto_form.html', {
        'formulario': formulario,
        'objeto': objeto,
        'acao': 'Solicitar Edição',
        'is_edicao_pendente': True,
    })


@login_required
def objeto_excluir(requisicao, pk):
    objeto = get_object_or_404(Objeto, pk=pk)

    if not pode_gerenciar_recurso(requisicao.user, objeto.usuario):
        messages.error(requisicao, 'Você não tem permissão para excluir este registro.')
        return redirect('meus_registros')

    if objeto.status == 'devolvido':
        messages.warning(requisicao, 'Este item não pode mais ser excluído.')
        return redirect('objeto_detail', pk=objeto.pk)

    if requisicao.method == 'POST':
        objeto.delete()
        messages.success(requisicao, 'Item excluído com sucesso.')
        return redirect('meus_registros')

    return render(requisicao, 'core/confirm_delete.html', {
        'objeto': objeto,
        'tipo_nome': 'item',
        'rota_cancelar': 'objeto_detail',
    })


@login_required
@papel_obrigatorio('admin')
def objeto_marcar_devolvido(requisicao, pk):
    objeto = get_object_or_404(Objeto, pk=pk)

    if requisicao.method == 'POST':
        if objeto.status == 'ativo':
            objeto.status = 'devolvido'
            objeto.save(update_fields=['status'])
            messages.success(requisicao, f'Item "{objeto.titulo}" marcado como devolvido.')
        else:
            messages.warning(requisicao, 'Este item não pode ser marcado como devolvido.')

    return redirect('objeto_detail', pk=objeto.pk)


