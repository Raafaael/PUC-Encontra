from django import forms
from django.contrib.auth.models import User

from ..models import Perfil

EMAIL_DUPLICATE_ERROR = 'Já existe uma conta com este e-mail.'
PERFIL_DUPLICATE_ERRORS = {
    'matricula': 'Já existe uma conta com esta matrícula.',
    'telefone': 'Já existe uma conta com este telefone.',
}
PERFIL_REQUIRED_ERRORS = {
    'telefone': 'Informe um telefone para contato.',
}


def clean_unique_user_email(email, *, exclude_user_pk=None):
    email = (email or '').strip()
    qs = User.objects.filter(email__iexact=email)
    if exclude_user_pk is not None:
        qs = qs.exclude(pk=exclude_user_pk)
    if qs.exists():
        raise forms.ValidationError(EMAIL_DUPLICATE_ERROR)
    return email


def clean_unique_perfil_field(field_name, value, *, exclude_perfil_pk=None, required=False):
    value = (value or '').strip()
    if required and not value:
        raise forms.ValidationError(PERFIL_REQUIRED_ERRORS[field_name])

    if value:
        qs = Perfil.objects.filter(**{field_name: value})
        if exclude_perfil_pk is not None:
            qs = qs.exclude(pk=exclude_perfil_pk)
        if qs.exists():
            raise forms.ValidationError(PERFIL_DUPLICATE_ERRORS[field_name])

    return value


class BasePerfilForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True, label='Nome')
    last_name = forms.CharField(max_length=100, required=True, label='Sobrenome')
    email = forms.EmailField(required=True, label='E-mail')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['telefone'].required = True

        user = getattr(self.instance, 'user', None)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    def clean_email(self):
        exclude_user_pk = self.instance.user.pk if getattr(self.instance, 'user_id', None) else None
        return clean_unique_user_email(
            self.cleaned_data.get('email'),
            exclude_user_pk=exclude_user_pk,
        )

    def clean_matricula(self):
        return clean_unique_perfil_field(
            'matricula',
            self.cleaned_data.get('matricula'),
            exclude_perfil_pk=self.instance.pk,
        )

    def clean_telefone(self):
        return clean_unique_perfil_field(
            'telefone',
            self.cleaned_data.get('telefone'),
            exclude_perfil_pk=self.instance.pk,
            required=True,
        )

    def _apply_user_data(self, perfil):
        perfil.user.first_name = self.cleaned_data['first_name']
        perfil.user.last_name = self.cleaned_data['last_name']
        perfil.user.email = self.cleaned_data['email']

    def save(self, commit=True):
        perfil = super().save(commit=False)
        self._apply_user_data(perfil)
        if commit:
            perfil.user.save()
            perfil.save()
        return perfil
