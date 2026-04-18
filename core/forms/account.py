from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from ..models import Perfil
from .shared import BasePerfilForm, limpar_campo_unico_perfil, limpar_email_unico_usuario


class RegistroForm(UserCreationForm):
    """Registro público: cria contas padrão de usuário."""

    email = User._meta.get_field('email').formfield(required=True, label='E-mail')
    first_name = User._meta.get_field('first_name').formfield(
        max_length=100,
        required=True,
        label='Nome',
    )
    last_name = User._meta.get_field('last_name').formfield(
        max_length=100,
        required=True,
        label='Sobrenome',
    )
    matricula = Perfil._meta.get_field('matricula').formfield(
        max_length=20,
        required=False,
        label='Matrícula',
    )
    telefone = Perfil._meta.get_field('telefone').formfield(
        max_length=20,
        required=True,
        label='Telefone',
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        return limpar_email_unico_usuario(self.cleaned_data.get('email'))

    def clean_matricula(self):
        return limpar_campo_unico_perfil('matricula', self.cleaned_data.get('matricula'))

    def clean_telefone(self):
        return limpar_campo_unico_perfil(
            'telefone',
            self.cleaned_data.get('telefone'),
            obrigatorio=True,
        )

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data['email']
        usuario.first_name = self.cleaned_data['first_name']
        usuario.last_name = self.cleaned_data['last_name']
        if commit:
            usuario.save()
            self.salvar_perfil(usuario)
        return usuario

    def salvar_perfil(self, usuario):
        Perfil.objects.update_or_create(
            user=usuario,
            defaults={
                'tipo': 'usuario',
                'matricula': self.cleaned_data.get('matricula', ''),
                'telefone': self.cleaned_data['telefone'],
            },
        )


class PerfilForm(BasePerfilForm):
    """Edição do perfil."""

    class Meta:
        model = Perfil
        fields = ['matricula', 'telefone']
