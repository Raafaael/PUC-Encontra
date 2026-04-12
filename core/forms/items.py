from django import forms

from ..models import ObjetoEncontrado, ObjetoPerdido


class ObjetoPerdidoForm(forms.ModelForm):
    """Cadastro e edição de objetos perdidos."""

    data_perda = forms.DateField(
        label='Data da perda',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta:
        model = ObjetoPerdido
        fields = ['titulo', 'descricao', 'categoria', 'local_perdido', 'data_perda', 'imagem']


class ObjetoEncontradoForm(forms.ModelForm):
    """Cadastro e edição de objetos encontrados."""

    data_encontrado = forms.DateField(
        label='Data que encontrou',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta:
        model = ObjetoEncontrado
        fields = ['titulo', 'descricao', 'categoria', 'local_encontrado', 'data_encontrado', 'imagem']
