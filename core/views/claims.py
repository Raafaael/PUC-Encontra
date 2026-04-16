from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..access import get_user_tipo
from ..decorators import role_required
from ..forms import SolicitacaoForm, ValidarSolicitacaoForm
from ..models import ObjetoEncontrado, SolicitacaoPosse


@login_required
def solicitacao_create(request, encontrado_id):
    objeto_encontrado = get_object_or_404(ObjetoEncontrado, pk=encontrado_id)

    if SolicitacaoPosse.objects.filter(
        solicitante=request.user,
        objeto_encontrado=objeto_encontrado,
    ).exists():
        messages.warning(request, 'Você já enviou uma solicitação para este item.')
        return redirect('objeto_encontrado_detail', pk=encontrado_id)

    if objeto_encontrado.status != 'disponivel':
        messages.warning(request, 'Este item não está mais disponível para solicitação.')
        return redirect('objeto_encontrado_detail', pk=encontrado_id)

    if request.method == 'POST':
        form = SolicitacaoForm(request.POST, user=request.user)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.solicitante = request.user
            solicitacao.objeto_encontrado = objeto_encontrado

            try:
                with transaction.atomic():
                    solicitacao.save()
                    objeto_encontrado.status = 'reivindicado'
                    objeto_encontrado.save(update_fields=['status'])
            except IntegrityError:
                messages.warning(request, 'Você já enviou uma solicitação para este item.')
                return redirect('objeto_encontrado_detail', pk=encontrado_id)

            messages.success(
                request,
                'Solicitação de posse enviada. Aguarde a validação do administrador.',
            )
            return redirect('solicitacao_detail', pk=solicitacao.pk)
    else:
        form = SolicitacaoForm(user=request.user)

    return render(request, 'core/solicitacao_form.html', {
        'form': form,
        'objeto_encontrado': objeto_encontrado,
    })


@login_required
def solicitacao_detail(request, pk):
    solicitacao = get_object_or_404(SolicitacaoPosse, pk=pk)
    tipo = get_user_tipo(request.user)

    if (
        tipo != 'admin'
        and solicitacao.solicitante != request.user
        and solicitacao.objeto_encontrado.usuario != request.user
    ):
        messages.error(request, 'Você não tem permissão para ver esta solicitação.')
        return redirect('meus_registros')

    return render(request, 'core/solicitacao_detail.html', {
        'solicitacao': solicitacao,
        'tipo': tipo,
    })


@login_required
@role_required('admin')
def solicitacao_validar(request, pk):
    solicitacao = get_object_or_404(SolicitacaoPosse, pk=pk)

    if solicitacao.status != 'pendente':
        messages.warning(request, 'Esta solicitação já foi avaliada.')
        return redirect('solicitacao_detail', pk=pk)

    if request.method == 'POST':
        form = ValidarSolicitacaoForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                solicitacao.status = form.cleaned_data['status']
                solicitacao.resposta_admin = form.cleaned_data['resposta_admin']
                solicitacao.data_resposta = timezone.now()
                solicitacao.save()

                if solicitacao.status == 'aprovada':
                    solicitacao.objeto_encontrado.status = 'devolvido'
                    solicitacao.objeto_encontrado.save(update_fields=['status'])
                    if solicitacao.objeto_perdido:
                        solicitacao.objeto_perdido.status = 'encontrado'
                        solicitacao.objeto_perdido.save(update_fields=['status'])
                    messages.success(request, 'Solicitação aprovada. Objeto marcado como devolvido.')
                else:
                    outras_pendentes = SolicitacaoPosse.objects.filter(
                        objeto_encontrado=solicitacao.objeto_encontrado,
                        status='pendente',
                    ).exclude(pk=pk).exists()
                    if not outras_pendentes:
                        solicitacao.objeto_encontrado.status = 'disponivel'
                        solicitacao.objeto_encontrado.save(update_fields=['status'])
                    messages.info(request, 'Solicitação rejeitada.')

            return redirect('aprovacoes')
    else:
        form = ValidarSolicitacaoForm()

    return render(request, 'core/solicitacao_validar.html', {
        'form': form,
        'solicitacao': solicitacao,
    })
