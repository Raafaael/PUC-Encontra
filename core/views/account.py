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

CHAVE_SESSAO_CADASTRO_PENDENTE = 'cadastro_pendente'


def montar_cadastro_pendente(formulario):
    return {
        'nome_usuario': formulario.cleaned_data['username'],
        'nome': formulario.cleaned_data['first_name'],
        'sobrenome': formulario.cleaned_data['last_name'],
        'email': formulario.cleaned_data['email'],
        'senha': make_password(formulario.cleaned_data['password1']),
        'matricula': formulario.cleaned_data.get('matricula', ''),
        'telefone': formulario.cleaned_data['telefone'],
        'tipo_cadastro': formulario.cleaned_data.get('tipo_cadastro', 'usuario'),
        'codigo_admin': formulario.cleaned_data.get('codigo_admin', ''),
        'codigo': CodigoVerificacao.gerar_codigo(),
        'criado_em': timezone.now().isoformat(),
    }


def obter_cadastro_pendente(requisicao):
    return requisicao.session.get(CHAVE_SESSAO_CADASTRO_PENDENTE)


def salvar_cadastro_pendente(requisicao, cadastro_pendente):
    requisicao.session[CHAVE_SESSAO_CADASTRO_PENDENTE] = cadastro_pendente
    requisicao.session.modified = True


def limpar_cadastro_pendente(requisicao):
    requisicao.session.pop(CHAVE_SESSAO_CADASTRO_PENDENTE, None)


def cadastro_pendente_expirou(cadastro_pendente):
    criado_em = cadastro_pendente.get('criado_em')
    if not criado_em:
        return True

    data_criacao = datetime.fromisoformat(criado_em)
    if timezone.is_naive(data_criacao):
        data_criacao = timezone.make_aware(
            data_criacao,
            timezone.get_current_timezone(),
        )

    return timezone.now() > data_criacao + timedelta(minutes=30)


def obter_erro_conflito_cadastro(cadastro_pendente):
    if User.objects.filter(username=cadastro_pendente['nome_usuario']).exists():
        return 'Este nome de usuário acabou de ser utilizado. Faça um novo cadastro.'
    if User.objects.filter(email__iexact=cadastro_pendente['email']).exists():
        return 'Este e-mail já está em uso. Faça um novo cadastro.'
    if cadastro_pendente.get('matricula') and Perfil.objects.filter(
        matricula=cadastro_pendente['matricula']
    ).exists():
        return 'Esta matrícula já está em uso. Faça um novo cadastro.'
    if Perfil.objects.filter(telefone=cadastro_pendente['telefone']).exists():
        return 'Este telefone já está em uso. Faça um novo cadastro.'
    return None


def enviar_email_verificacao(cadastro_pendente, *, reenviar=False):
    nome_destinatario = cadastro_pendente['nome']
    codigo_verificacao = cadastro_pendente['codigo']
    assunto = (
        'PUC Encontra - Novo Código de Verificação'
        if reenviar
        else 'PUC Encontra - Código de Verificação'
    )

    send_mail(
        subject=assunto,
        message=(
            f'Olá, {nome_destinatario}!\n\n'
            f'Seu código de verificação é: {codigo_verificacao}\n\n'
            'Digite este código na página de verificação para concluir seu cadastro.\n'
            'O código expira em 30 minutos.\n\n'
            'Atenciosamente,\n'
            'Equipe PUC Encontra'
        ),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[cadastro_pendente['email']],
    )


def registro(requisicao):
    if requisicao.user.is_authenticated:
        return redirect('dashboard')

    if requisicao.method == 'POST':
        formulario = RegistroForm(requisicao.POST)
        if formulario.is_valid():
            if not settings.REGISTRO_EXIGE_VERIFICACAO_EMAIL:
                limpar_cadastro_pendente(requisicao)
                usuario = formulario.save()
                login(
                    requisicao,
                    usuario,
                    backend='core.backends.EmailOuUsernameBackend',
                )
                messages.success(
                    requisicao,
                    f'Bem-vindo(a), {usuario.first_name}! Conta criada com sucesso.',
                )
                return redirect('dashboard')

            cadastro_pendente = montar_cadastro_pendente(formulario)
            salvar_cadastro_pendente(requisicao, cadastro_pendente)
            enviar_email_verificacao(cadastro_pendente)
            return redirect('verificar_email')
    else:
        formulario = RegistroForm()

    return render(requisicao, 'registration/registro.html', {'formulario': formulario})


def verificar_email(requisicao):
    if not settings.REGISTRO_EXIGE_VERIFICACAO_EMAIL:
        limpar_cadastro_pendente(requisicao)
        return redirect('registro')

    cadastro_pendente = obter_cadastro_pendente(requisicao)
    if not cadastro_pendente:
        return redirect('registro')

    erro = None
    if requisicao.method == 'POST':
        if 'reenviar' in requisicao.POST:
            cadastro_pendente['codigo'] = CodigoVerificacao.gerar_codigo()
            cadastro_pendente['criado_em'] = timezone.now().isoformat()
            salvar_cadastro_pendente(requisicao, cadastro_pendente)
            enviar_email_verificacao(cadastro_pendente, reenviar=True)
            messages.success(requisicao, 'Novo código enviado para seu e-mail.')
            return redirect('verificar_email')

        codigo_digitado = requisicao.POST.get('codigo', '').strip()
        if cadastro_pendente_expirou(cadastro_pendente):
            erro = 'Código expirado. Solicite um novo código.'
        elif cadastro_pendente['codigo'] != codigo_digitado:
            erro = 'Código incorreto. Tente novamente.'
        else:
            erro_conflito = obter_erro_conflito_cadastro(cadastro_pendente)
            if erro_conflito:
                limpar_cadastro_pendente(requisicao)
                messages.error(requisicao, erro_conflito)
                return redirect('registro')

            usuario = User(
                username=cadastro_pendente['nome_usuario'],
                first_name=cadastro_pendente['nome'],
                last_name=cadastro_pendente['sobrenome'],
                email=cadastro_pendente['email'],
                password=cadastro_pendente['senha'],
                is_active=True,
            )
            usuario.save()

            Perfil.objects.update_or_create(
                user=usuario,
                defaults={
                    'tipo': cadastro_pendente.get('tipo_cadastro', 'usuario'),
                    'matricula': cadastro_pendente.get('matricula', ''),
                    'telefone': cadastro_pendente['telefone'],
                },
            )

            limpar_cadastro_pendente(requisicao)
            login(requisicao, usuario, backend='core.backends.EmailOuUsernameBackend')
            messages.success(
                requisicao,
                f'Bem-vindo(a), {usuario.first_name}! Conta verificada com sucesso.',
            )
            return redirect('dashboard')

    return render(
        requisicao,
        'registration/verificar_email.html',
        {
            'email': cadastro_pendente['email'],
            'erro': erro,
        },
    )


@login_required
def perfil(requisicao):
    perfil_usuario = Perfil.objects.get_or_create(
        user=requisicao.user,
        defaults={'tipo': 'usuario'},
    )[0]

    if requisicao.method == 'POST':
        formulario = PerfilForm(requisicao.POST, instance=perfil_usuario)
        if formulario.is_valid():
            formulario.save()
            messages.success(requisicao, 'Perfil atualizado com sucesso.')
            return redirect('perfil')
    else:
        formulario = PerfilForm(instance=perfil_usuario)

    return render(requisicao, 'core/perfil.html', {'formulario': formulario})


@login_required
def trocar_senha(requisicao):
    if requisicao.method == 'POST':
        formulario = PasswordChangeForm(requisicao.user, requisicao.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            update_session_auth_hash(requisicao, usuario)
            messages.success(requisicao, 'Senha alterada com sucesso.')
            return redirect('perfil')
    else:
        formulario = PasswordChangeForm(requisicao.user)

    return render(requisicao, 'core/trocar_senha.html', {'formulario': formulario})


@login_required
def desativar_conta(requisicao):
    if requisicao.method == 'POST':
        requisicao.user.is_active = False
        requisicao.user.save(update_fields=['is_active'])
        logout(requisicao)
        messages.info(
            requisicao,
            'Sua conta foi desativada. Entre em contato com o administrador para reativá-la.',
        )
        return redirect('home')

    return render(requisicao, 'core/desativar_conta.html')
