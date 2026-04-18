from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils import timezone

from ..forms import PerfilForm, RegistroForm
from ..models import CodigoVerificacao, Perfil

PENDING_REGISTRATION_SESSION_KEY = 'pending_registration'


def _build_pending_registration(form):
    return {
        'username': form.cleaned_data['username'],
        'first_name': form.cleaned_data['first_name'],
        'last_name': form.cleaned_data['last_name'],
        'email': form.cleaned_data['email'],
        'password': make_password(form.cleaned_data['password1']),
        'matricula': form.cleaned_data.get('matricula', ''),
        'telefone': form.cleaned_data['telefone'],
        'tipo_cadastro': form.cleaned_data.get('tipo_cadastro', 'usuario'),
        'codigo_admin': form.cleaned_data.get('codigo_admin', ''),
        'codigo': CodigoVerificacao.gerar_codigo(),
        'criado_em': timezone.now().isoformat(),
    }


def _get_pending_registration(request):
    return request.session.get(PENDING_REGISTRATION_SESSION_KEY)


def _save_pending_registration(request, pending_registration):
    request.session[PENDING_REGISTRATION_SESSION_KEY] = pending_registration
    request.session.modified = True


def _clear_pending_registration(request):
    request.session.pop(PENDING_REGISTRATION_SESSION_KEY, None)


def _pending_registration_expired(pending_registration):
    created_at = pending_registration.get('criado_em')
    if not created_at:
        return True

    created_at_dt = datetime.fromisoformat(created_at)
    if timezone.is_naive(created_at_dt):
        created_at_dt = timezone.make_aware(created_at_dt, timezone.get_current_timezone())

    return timezone.now() > created_at_dt + timedelta(minutes=30)


def _pending_registration_conflict(pending_registration):
    if User.objects.filter(username=pending_registration['username']).exists():
        return 'Este nome de usuário acabou de ser utilizado. Faça um novo cadastro.'
    if User.objects.filter(email__iexact=pending_registration['email']).exists():
        return 'Este e-mail já está em uso. Faça um novo cadastro.'
    if pending_registration.get('matricula') and Perfil.objects.filter(
        matricula=pending_registration['matricula']
    ).exists():
        return 'Esta matrícula já está em uso. Faça um novo cadastro.'
    if Perfil.objects.filter(telefone=pending_registration['telefone']).exists():
        return 'Este telefone já está em uso. Faça um novo cadastro.'
    return None


def _send_verification_email(pending_registration, *, resend=False):
    greeting_name = pending_registration['first_name']
    verification_code = pending_registration['codigo']
    subject = (
        'PUC Encontra - Novo Código de Verificação'
        if resend
        else 'PUC Encontra - Código de Verificação'
    )
    send_mail(
        subject=subject,
        message=(
            f'Olá, {greeting_name}!\n\n'
            f'Seu código de verificação é: {verification_code}\n\n'
            'Digite este código na página de verificação para concluir seu cadastro.\n'
            'O código expira em 30 minutos.\n\n'
            'Atenciosamente,\n'
            'Equipe PUC Encontra'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[pending_registration['email']],
    )


def registro(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            pending_registration = _build_pending_registration(form)
            _save_pending_registration(request, pending_registration)
            _send_verification_email(pending_registration)
            return redirect('verificar_email')
    else:
        form = RegistroForm()

    return render(request, 'registration/registro.html', {'form': form})


def verificar_email(request):
    pending_registration = _get_pending_registration(request)
    if not pending_registration:
        return redirect('registro')

    erro = None
    if request.method == 'POST':
        if 'reenviar' in request.POST:
            pending_registration['codigo'] = CodigoVerificacao.gerar_codigo()
            pending_registration['criado_em'] = timezone.now().isoformat()
            _save_pending_registration(request, pending_registration)
            _send_verification_email(pending_registration, resend=True)
            messages.success(request, 'Novo código enviado para seu e-mail.')
            return redirect('verificar_email')

        codigo_digitado = request.POST.get('codigo', '').strip()
        if _pending_registration_expired(pending_registration):
            erro = 'Código expirado. Solicite um novo código.'
        elif pending_registration['codigo'] != codigo_digitado:
            erro = 'Código incorreto. Tente novamente.'
        else:
            conflict_error = _pending_registration_conflict(pending_registration)
            if conflict_error:
                _clear_pending_registration(request)
                messages.error(request, conflict_error)
                return redirect('registro')

            user = User(
                username=pending_registration['username'],
                first_name=pending_registration['first_name'],
                last_name=pending_registration['last_name'],
                email=pending_registration['email'],
                password=pending_registration['password'],
                is_active=True,
            )
            user.save()
            Perfil.objects.update_or_create(
                user=user,
                defaults={
                    'tipo': pending_registration.get('tipo_cadastro', 'usuario'),
                    'matricula': pending_registration.get('matricula', ''),
                    'telefone': pending_registration['telefone'],
                },
            )
            _clear_pending_registration(request)
            login(request, user, backend='core.backends.EmailOuUsernameBackend')
            messages.success(request, f'Bem-vindo(a), {user.first_name}! Conta verificada com sucesso.')
            return redirect('dashboard')

    return render(request, 'registration/verificar_email.html', {
        'email': pending_registration['email'],
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
