from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..access import obter_tipo_usuario
from ..decorators import papel_obrigatorio
from ..forms import SolicitacaoForm, ValidarSolicitacaoForm
from ..models import Objeto, SolicitacaoPosse


@login_required
def solicitacao_criar(requisicao, objeto_id):
    objeto = get_object_or_404(Objeto, pk=objeto_id, tipo='encontrado')

    if SolicitacaoPosse.objects.filter(
        solicitante=requisicao.user,
        objeto=objeto,
    ).exists():
        messages.warning(requisicao, 'Você já enviou uma solicitação para este item.')
        return redirect('objeto_detail', pk=objeto_id)

    if objeto.status != 'ativo':
        messages.warning(requisicao, 'Este item não está mais disponível para solicitação.')
        return redirect('objeto_detail', pk=objeto_id)

    if requisicao.method == 'POST':
        formulario = SolicitacaoForm(requisicao.POST, usuario=requisicao.user)
        if formulario.is_valid():
            solicitacao = formulario.save(commit=False)
            solicitacao.solicitante = requisicao.user
            solicitacao.objeto = objeto

            try:
                with transaction.atomic():
                    solicitacao.save()
                    objeto.status = 'reivindicado'
                    objeto.save(update_fields=['status'])
            except IntegrityError:
                messages.warning(requisicao, 'Você já enviou uma solicitação para este item.')
                return redirect('objeto_detail', pk=objeto_id)

            messages.success(
                requisicao,
                'Solicitação de posse enviada. Aguarde a validação do administrador.',
            )
            return redirect('solicitacao_detail', pk=solicitacao.pk)
    else:
        formulario = SolicitacaoForm(usuario=requisicao.user)

    return render(requisicao, 'core/solicitacao_form.html', {
        'formulario': formulario,
        'objeto': objeto,
    })


@login_required
def solicitacao_detalhe(requisicao, pk):
    solicitacao = get_object_or_404(SolicitacaoPosse, pk=pk)
    tipo_usuario = obter_tipo_usuario(requisicao.user)

    if (
        tipo_usuario != 'admin'
        and solicitacao.solicitante != requisicao.user
        and solicitacao.objeto.usuario != requisicao.user
    ):
        messages.error(requisicao, 'Você não tem permissão para ver esta solicitação.')
        return redirect('meus_registros')

    return render(requisicao, 'core/solicitacao_detail.html', {
        'solicitacao': solicitacao,
        'tipo': tipo_usuario,
    })


@login_required
@papel_obrigatorio('admin')
def solicitacao_avaliar(requisicao, pk):
    solicitacao = get_object_or_404(SolicitacaoPosse, pk=pk)

    if solicitacao.status != 'pendente':
        messages.warning(requisicao, 'Esta solicitação já foi avaliada.')
        return redirect('solicitacao_detail', pk=pk)

    if requisicao.method == 'POST':
        formulario = ValidarSolicitacaoForm(requisicao.POST)
        if formulario.is_valid():
            with transaction.atomic():
                solicitacao.status = formulario.cleaned_data['status']
                solicitacao.resposta_admin = formulario.cleaned_data['resposta_admin']
                solicitacao.data_resposta = timezone.now()
                solicitacao.save()

                if solicitacao.status == 'aprovada':
                    solicitacao.objeto.status = 'devolvido'
                    solicitacao.objeto.save(update_fields=['status'])
                    messages.success(requisicao, 'Solicitação aprovada. Objeto marcado como devolvido.')
                else:
                    outras_pendentes = SolicitacaoPosse.objects.filter(
                        objeto=solicitacao.objeto,
                        status='pendente',
                    ).exclude(pk=pk).exists()
                    if not outras_pendentes:
                        solicitacao.objeto.status = 'ativo'
                        solicitacao.objeto.save(update_fields=['status'])
                    messages.info(requisicao, 'Solicitação rejeitada.')

            return redirect('aprovacoes')
    else:
        formulario = ValidarSolicitacaoForm()

    return render(requisicao, 'core/solicitacao_validar.html', {
        'formulario': formulario,
        'solicitacao': solicitacao,
    })
