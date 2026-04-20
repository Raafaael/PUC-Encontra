from django import forms

from ..models import Objeto


class ObjetoForm(forms.ModelForm):
    """Cadastro e edição de objetos (perdidos ou encontrados)."""

    tipo = forms.ChoiceField(
        label='Tipo de solicitação',
        choices=Objeto.TIPO_CHOICES,
        widget=forms.RadioSelect,
    )

    data_ocorrencia = forms.DateField(
        label='Data da ocorrência',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta:
        model = Objeto
        fields = ['tipo', 'titulo', 'descricao', 'categoria', 'local', 'data_ocorrencia', 'imagem']
