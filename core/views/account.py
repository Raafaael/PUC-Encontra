from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from ..forms import PerfilForm, RegistroForm
from ..models import CodigoVerificacao, Perfil


def registro(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            form.save_perfil(user)

            codigo = CodigoVerificacao.gerar_codigo()
            CodigoVerificacao.objects.update_or_create(
                user=user, defaults={'codigo': codigo},
            )
            send_mail(
                subject='PUC Encontra - Código de Verificação',
                message=(
                    f'Olá, {user.first_name}!\n\n'
                    f'Seu código de verificação é: {codigo}\n\n'
                    'Digite este código na página de verificação para ativar sua conta.\n'
                    'O código expira em 30 minutos.\n\n'
                    'Atenciosamente,\n'
                    'Equipe PUC Encontra'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            request.session['user_id_verificacao'] = user.pk
            return redirect('verificar_email')
    else:
        form = RegistroForm()

    return render(request, 'registration/registro.html', {'form': form})


def verificar_email(request):
    user_id = request.session.get('user_id_verificacao')
    if not user_id:
        return redirect('registro')

    from django.contrib.auth.models import User
    try:
        user = User.objects.get(pk=user_id, is_active=False)
    except User.DoesNotExist:
        request.session.pop('user_id_verificacao', None)
        return redirect('registro')

    erro = None
    if request.method == 'POST':
        if 'reenviar' in request.POST:
            codigo = CodigoVerificacao.gerar_codigo()
            CodigoVerificacao.objects.update_or_create(
                user=user, defaults={'codigo': codigo},
            )
            send_mail(
                subject='PUC Encontra - Novo Código de Verificação',
                message=(
                    f'Olá, {user.first_name}!\n\n'
                    f'Seu novo código de verificação é: {codigo}\n\n'
                    'O código expira em 30 minutos.\n\n'
                    'Atenciosamente,\n'
                    'Equipe PUC Encontra'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            messages.success(request, 'Novo código enviado para seu e-mail.')
            return redirect('verificar_email')

        codigo_digitado = request.POST.get('codigo', '').strip()
        try:
            verificacao = CodigoVerificacao.objects.get(user=user)
        except CodigoVerificacao.DoesNotExist:
            erro = 'Código não encontrado. Solicite um novo código.'
        else:
            if verificacao.expirado():
                erro = 'Código expirado. Solicite um novo código.'
            elif verificacao.codigo != codigo_digitado:
                erro = 'Código incorreto. Tente novamente.'
            else:
                user.is_active = True
                user.save(update_fields=['is_active'])
                verificacao.delete()
                request.session.pop('user_id_verificacao', None)
                login(request, user, backend='core.backends.EmailOuUsernameBackend')
                messages.success(request, f'Bem-vindo(a), {user.first_name}! Conta verificada com sucesso.')
                return redirect('dashboard')

    return render(request, 'registration/verificar_email.html', {
        'email': user.email,
        'erro': erro,
    })


@login_required
def perfil(request):
    perfil_obj, _ = Perfil.objects.get_or_create(user=request.user, defaults={'tipo': 'usuario'})

    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=perfil_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso.')
            return redirect('perfil')
    else:
        form = PerfilForm(instance=perfil_obj)

    return render(request, 'core/perfil.html', {'form': form})


@login_required
def trocar_senha(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Senha alterada com sucesso.')
            return redirect('perfil')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'core/trocar_senha.html', {'form': form})


@login_required
def desativar_conta(request):
    if request.method == 'POST':
        request.user.is_active = False
        request.user.save(update_fields=['is_active'])
        logout(request)
        messages.info(
            request,
            'Sua conta foi desativada. Entre em contato com o administrador para reativá-la.',
        )
        return redirect('home')

    return render(request, 'core/desativar_conta.html')
