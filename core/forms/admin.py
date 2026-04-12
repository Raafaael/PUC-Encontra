from django import forms

from ..models import Categoria, Local, Perfil
from .shared import BasePerfilForm


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
