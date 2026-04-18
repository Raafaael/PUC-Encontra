from django import forms

from ..models import ObjetoPerdido, SolicitacaoPosse


class SolicitacaoForm(forms.ModelForm):
    """Solicitação de posse sobre um objeto encontrado."""

    class Meta:
        model = SolicitacaoPosse
        fields = ['objeto_perdido', 'descricao_comprovacao']
        widgets = {
            'descricao_comprovacao': forms.Textarea(attrs={
                'placeholder': (
                    'Descreva características que comprovem que o objeto é seu '
                    '(cor, marca, modelo, algum detalhe específico...)'
                )
            }),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['objeto_perdido'].queryset = ObjetoPerdido.objects.filter(
                usuario=usuario,
                status='aberto',
            )
        self.fields['objeto_perdido'].required = False
        self.fields['objeto_perdido'].empty_label = '(Nenhum - não registrei a perda)'


class ValidarSolicitacaoForm(forms.Form):
    """Admin aprova ou rejeita uma solicitação."""

    status = forms.ChoiceField(
        choices=[('aprovada', 'Aprovar'), ('rejeitada', 'Rejeitar')],
        widget=forms.RadioSelect,
        label='Decisão',
    )
    resposta_admin = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Justificativa da decisão...'}),
        label='Resposta',
        required=False,
    )
