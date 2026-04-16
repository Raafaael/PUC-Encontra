from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import (
    Categoria,
    Local,
    ObjetoEncontrado,
    ObjetoPerdido,
    Perfil,
    SolicitacaoPosse,
)


class RegistroForm(UserCreationForm):
    """Registro público: cria contas padrão de usuário."""

    email = forms.EmailField(required=True, label='E-mail')
    first_name = forms.CharField(max_length=100, required=True, label='Nome')
    last_name = forms.CharField(max_length=100, required=True, label='Sobrenome')
    matricula = forms.CharField(max_length=20, required=False, label='Matrícula')
    telefone = forms.CharField(max_length=20, required=True, label='Telefone')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Já existe uma conta com este e-mail.')
        return email

    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula', '').strip()
        if matricula and Perfil.objects.filter(matricula=matricula).exists():
            raise forms.ValidationError('Já existe uma conta com esta matrícula.')
        return matricula

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone', '').strip()
        if not telefone:
            raise forms.ValidationError('Informe um telefone para contato.')
        if Perfil.objects.filter(telefone=telefone).exists():
            raise forms.ValidationError('Já existe uma conta com este telefone.')
        return telefone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            self.save_perfil(user)
        return user

    def save_perfil(self, user):
        Perfil.objects.update_or_create(
            user=user,
            defaults={
                'tipo': 'usuario',
                'matricula': self.cleaned_data.get('matricula', ''),
                'telefone': self.cleaned_data['telefone'],
            },
        )


class PerfilForm(forms.ModelForm):
    """Edição do perfil."""

    first_name = forms.CharField(max_length=100, required=True, label='Nome')
    last_name = forms.CharField(max_length=100, required=True, label='Sobrenome')
    email = forms.EmailField(required=True, label='E-mail')

    class Meta:
        model = Perfil
        fields = ['matricula', 'telefone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['telefone'].required = True
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise forms.ValidationError('Já existe uma conta com este e-mail.')
        return email

    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula', '').strip()
        if matricula:
            qs = Perfil.objects.filter(matricula=matricula).exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Já existe uma conta com esta matrícula.')
        return matricula

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone', '').strip()
        if not telefone:
            raise forms.ValidationError('Informe um telefone para contato.')
        qs = Perfil.objects.filter(telefone=telefone).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Já existe uma conta com este telefone.')
        return telefone

    def save(self, commit=True):
        perfil = super().save(commit=False)
        perfil.user.first_name = self.cleaned_data['first_name']
        perfil.user.last_name = self.cleaned_data['last_name']
        perfil.user.email = self.cleaned_data['email']
        if commit:
            perfil.user.save()
            perfil.save()
        return perfil


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

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['objeto_perdido'].queryset = ObjetoPerdido.objects.filter(
                usuario=user, status='aberto'
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


class AdminUsuarioForm(forms.ModelForm):
    """Admin edita dados e tipo de um usuário."""

    first_name = forms.CharField(max_length=100, label='Nome')
    last_name = forms.CharField(max_length=100, label='Sobrenome')
    email = forms.EmailField(label='E-mail')
    is_active = forms.BooleanField(required=False, label='Usuário ativo')

    class Meta:
        model = Perfil
        fields = ['tipo', 'matricula', 'telefone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['telefone'].required = True
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['is_active'].initial = self.instance.user.is_active

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise forms.ValidationError('Já existe uma conta com este e-mail.')
        return email

    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula', '').strip()
        if matricula:
            qs = Perfil.objects.filter(matricula=matricula).exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Já existe uma conta com esta matrícula.')
        return matricula

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone', '').strip()
        if not telefone:
            raise forms.ValidationError('Informe um telefone para contato.')
        qs = Perfil.objects.filter(telefone=telefone).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Já existe uma conta com este telefone.')
        return telefone

    def save(self, commit=True):
        perfil = super().save(commit=False)
        perfil.user.first_name = self.cleaned_data['first_name']
        perfil.user.last_name = self.cleaned_data['last_name']
        perfil.user.email = self.cleaned_data['email']
        perfil.user.is_active = self.cleaned_data['is_active']
        if commit:
            perfil.user.save()
            perfil.save()
        return perfil
