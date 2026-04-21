from django import forms
from django.utils import timezone

from ..models import Objeto, SolicitacaoEdicao


def validar_data_nao_futura(data):
    if not data:
        return data
    hoje = timezone.localdate()
    if data > hoje:
        raise forms.ValidationError('A data não pode ser no futuro.')
    if data < hoje.replace(year=hoje.year - 1):
        raise forms.ValidationError('A data não pode ser anterior a 1 ano atrás.')
    return data


class ObjetoForm(forms.ModelForm):
    tipo = forms.ChoiceField(
        label='Tipo de solicitação',
        choices=Objeto.TIPO_CHOICES,
        widget=forms.RadioSelect,
    )
    data_ocorrencia = forms.DateField(
        label='Data da ocorrência',
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
    )

    class Meta:
        model = Objeto
        fields = ['tipo', 'titulo', 'descricao', 'categoria', 'local', 'data_ocorrencia', 'imagem']

    def clean_data_ocorrencia(self):
        return validar_data_nao_futura(self.cleaned_data.get('data_ocorrencia'))


class EdicaoForm(forms.ModelForm):
    data_ocorrencia = forms.DateField(
        label='Data da ocorrência',
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
    )

    class Meta:
        model = SolicitacaoEdicao
        fields = ['titulo', 'descricao', 'categoria', 'local', 'data_ocorrencia', 'imagem']

    def clean_data_ocorrencia(self):
        return validar_data_nao_futura(self.cleaned_data.get('data_ocorrencia'))
