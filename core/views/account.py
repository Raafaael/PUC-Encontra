from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..forms import PerfilForm, RegistroForm
from ..models import Perfil


def registro(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='core.backends.EmailOrUsernameBackend')
            messages.success(request, f'Bem-vindo(a), {user.first_name}! Conta criada com sucesso.')
            return redirect('dashboard')
    else:
        form = RegistroForm()

    return render(request, 'registration/registro.html', {'form': form})


def verificar_email(request):
    email = request.user.email if request.user.is_authenticated else request.GET.get('email', '')
    return render(request, 'registration/verificar_email.html', {'email': email})


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
