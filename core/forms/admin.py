from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from ..models import Categoria, Local, Perfil
from .shared import BasePerfilForm, clean_unique_perfil_field, clean_unique_user_email


class AprovarItemForm(forms.Form):
    """Admin aprova ou rejeita um item antes de publicar."""

    acao = forms.ChoiceField(
        choices=[('aprovar', 'Aprovar e publicar'), ('rejeitar', 'Rejeitar')],
        widget=forms.RadioSelect,
        label='Decisão',
    )


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao']


class LocalForm(forms.ModelForm):
    class Meta:
        model = Local
        fields = ['nome', 'predio', 'andar', 'descricao']


class AdminUsuarioForm(BasePerfilForm):
    """Admin edita dados e tipo de um usuário."""

    is_active = forms.BooleanField(required=False, label='Usuário ativo')

    class Meta:
        model = Perfil
        fields = ['tipo', 'matricula', 'telefone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = getattr(self.instance, 'user', None)
        if user:
            self.fields['is_active'].initial = user.is_active

    def save(self, commit=True):
        perfil = super().save(commit=False)
        perfil.user.is_active = self.cleaned_data['is_active']
        if commit:
            perfil.user.save()
            perfil.save()
        return perfil


class AdminCreateForm(UserCreationForm):
    """Criação direta de uma nova conta administradora pelo painel admin."""

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
        return clean_unique_user_email(self.cleaned_data.get('email'))

    def clean_matricula(self):
        return clean_unique_perfil_field('matricula', self.cleaned_data.get('matricula'))

    def clean_telefone(self):
        return clean_unique_perfil_field(
            'telefone',
            self.cleaned_data.get('telefone'),
            required=True,
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
            self.save_perfil(user)
        return user

    def save_perfil(self, user):
        Perfil.objects.update_or_create(
            user=user,
            defaults={
                'tipo': 'admin',
                'matricula': self.cleaned_data.get('matricula', ''),
                'telefone': self.cleaned_data['telefone'],
            },
        )
