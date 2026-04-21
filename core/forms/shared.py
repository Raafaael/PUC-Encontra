from django import forms
from django.contrib.auth.models import User

from ..models import Perfil

ERRO_EMAIL_DUPLICADO = 'Já existe uma conta com este e-mail.'
ERROS_PERFIL_DUPLICADO = {
    'matricula': 'Já existe uma conta com esta matrícula.',
    'telefone': 'Já existe uma conta com este telefone.',
}
ERROS_PERFIL_OBRIGATORIO = {
    'telefone': 'Informe um telefone para contato.',
}


def limpar_email_unico_usuario(email, *, excluir_pk_usuario=None):
    email = (email or '').strip()
    consulta = User.objects.filter(email__iexact=email)
    if excluir_pk_usuario is not None:
        consulta = consulta.exclude(pk=excluir_pk_usuario)
    if consulta.exists():
        raise forms.ValidationError(ERRO_EMAIL_DUPLICADO)
    return email


def limpar_campo_unico_perfil(nome_campo, valor, *, excluir_pk_perfil=None, obrigatorio=False):
    valor_str = (str(valor) if valor else '').strip()
    if obrigatorio and not valor_str:
        raise forms.ValidationError(ERROS_PERFIL_OBRIGATORIO[nome_campo])

    if valor_str:
        consulta = Perfil.objects.filter(**{nome_campo: valor})
        if excluir_pk_perfil is not None:
            consulta = consulta.exclude(pk=excluir_pk_perfil)
        if consulta.exists():
            raise forms.ValidationError(ERROS_PERFIL_DUPLICADO[nome_campo])

    return valor


class BasePerfilForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True, label='Nome')
    last_name = forms.CharField(max_length=100, required=True, label='Sobrenome')
    email = forms.EmailField(required=True, label='E-mail')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['telefone'].required = True

        usuario = getattr(self.instance, 'user', None)
        if usuario:
            self.fields['first_name'].initial = usuario.first_name
            self.fields['last_name'].initial = usuario.last_name
            self.fields['email'].initial = usuario.email

    def clean_email(self):
        excluir_pk_usuario = self.instance.user.pk if getattr(self.instance, 'user_id', None) else None
        return limpar_email_unico_usuario(
            self.cleaned_data.get('email'),
            excluir_pk_usuario=excluir_pk_usuario,
        )

    def clean_matricula(self):
        return limpar_campo_unico_perfil(
            'matricula',
            self.cleaned_data.get('matricula'),
            excluir_pk_perfil=self.instance.pk,
        )

    def clean_telefone(self):
        return limpar_campo_unico_perfil(
            'telefone',
            self.cleaned_data.get('telefone'),
            excluir_pk_perfil=self.instance.pk,
            obrigatorio=True,
        )

    def aplicar_dados_usuario(self, perfil):
        perfil.user.first_name = self.cleaned_data['first_name']
        perfil.user.last_name = self.cleaned_data['last_name']
        perfil.user.email = self.cleaned_data['email']

    def save(self, commit=True):
        perfil = super().save(commit=False)
        self.aplicar_dados_usuario(perfil)
        if commit:
            perfil.user.save()
            perfil.save()
        return perfil
