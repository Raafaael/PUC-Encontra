import random

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Perfil(models.Model):
    """Perfil estendido do usuário com tipo de acesso."""

    TIPO_CHOICES = [
        ('usuario', 'Usuário'),
        ('admin', 'Administrador'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, default='usuario')
    matricula = models.CharField('Matrícula', max_length=20, blank=True)
    telefone = models.CharField('Telefone', max_length=20)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
        constraints = [
            models.UniqueConstraint(
                fields=['matricula'],
                condition=~models.Q(matricula=''),
                name='unique_perfil_matricula_not_blank',
            ),
            models.UniqueConstraint(
                fields=['telefone'],
                condition=~models.Q(telefone=''),
                name='unique_perfil_telefone_not_blank',
            ),
        ]

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} ({self.get_tipo_display()})'

    @property
    def eh_admin(self):
        return self.tipo == 'admin'

    @property
    def eh_funcionario(self):
        return False

    @property
    def eh_usuario(self):
        return self.tipo == 'usuario'

    @property
    def eh_aluno(self):
        return self.eh_usuario


class CodigoVerificacao(models.Model):
    """Código de 6 dígitos para verificação de e-mail no registro."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='codigo_verificacao')
    codigo = models.CharField(max_length=6)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Código de Verificação'
        verbose_name_plural = 'Códigos de Verificação'

    def __str__(self):
        return f'Código para {self.user.username}'

    @staticmethod
    def gerar_codigo():
        return f'{random.randint(0, 999999):06d}'

    def expirado(self):
        return timezone.now() > self.criado_em + timezone.timedelta(minutes=30)


class Categoria(models.Model):
    """Categoria de objetos."""

    nome = models.CharField('Nome', max_length=100, unique=True)
    descricao = models.TextField('Descrição', blank=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Local(models.Model):
    """Local dentro da universidade."""

    nome = models.CharField('Nome do Local', max_length=150)
    predio = models.CharField('Prédio', max_length=100)
    andar = models.CharField('Andar', max_length=20, blank=True)
    descricao = models.TextField('Descrição', blank=True)

    class Meta:
        verbose_name = 'Local'
        verbose_name_plural = 'Locais'
        ordering = ['predio', 'nome']
        unique_together = ['nome', 'predio']

    def __str__(self):
        partes = [self.nome]
        if self.predio:
            partes.append(f'- {self.predio}')
        if self.andar:
            partes.append(f'({self.andar})')
        return ' '.join(partes)


class Objeto(models.Model):
    """Registro unificado de objeto perdido ou encontrado."""

    TIPO_CHOICES = [
        ('perdido', 'Perdido'),
        ('encontrado', 'Encontrado'),
    ]

    STATUS_CHOICES = [
        ('pendente', 'Pendente de Aprovação'),
        ('ativo', 'Ativo'),
        ('reivindicado', 'Reivindicado'),
        ('devolvido', 'Devolvido'),
    ]

    tipo = models.CharField('Tipo', max_length=10, choices=TIPO_CHOICES)
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='objetos',
        verbose_name='Usuário',
    )
    titulo = models.CharField('Título', max_length=200)
    descricao = models.TextField('Descrição detalhada')
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        related_name='objetos',
        verbose_name='Categoria',
    )
    local = models.ForeignKey(
        Local,
        on_delete=models.SET_NULL,
        null=True,
        related_name='objetos',
        verbose_name='Local',
    )
    data_ocorrencia = models.DateField('Data da ocorrência')
    data_registro = models.DateTimeField('Data do registro', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Última atualização', auto_now=True)
    status = models.CharField('Status', max_length=15, choices=STATUS_CHOICES, default='pendente')
    imagem = models.ImageField('Imagem', upload_to='objetos/', blank=True, null=True)

    class Meta:
        verbose_name = 'Objeto'
        verbose_name_plural = 'Objetos'
        ordering = ['-data_registro']

    def __str__(self):
        return f'{self.titulo} ({self.get_tipo_display()})'


class SolicitacaoPosse(models.Model):
    """Solicitação de posse: usuário reivindica um objeto encontrado."""

    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
    ]

    solicitante = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='solicitacoes',
        verbose_name='Solicitante',
    )
    objeto = models.ForeignKey(
        Objeto,
        on_delete=models.CASCADE,
        related_name='solicitacoes',
        verbose_name='Objeto encontrado',
    )
    objeto_perdido = models.ForeignKey(
        Objeto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitacoes_como_perdido',
        verbose_name='Registro de perda relacionado',
        help_text='Opcional: vincule ao seu registro de perda, se houver.',
    )
    descricao_comprovacao = models.TextField(
        'Descrição de comprovação',
        help_text='Descreva características do objeto que comprovem que é seu.',
    )
    data_solicitacao = models.DateTimeField('Data da solicitação', auto_now_add=True)
    status = models.CharField('Status', max_length=10, choices=STATUS_CHOICES, default='pendente')
    resposta_admin = models.TextField('Resposta do administrador', blank=True)
    data_resposta = models.DateTimeField('Data da resposta', null=True, blank=True)

    class Meta:
        verbose_name = 'Solicitação de Posse'
        verbose_name_plural = 'Solicitações de Posse'
        ordering = ['-data_solicitacao']
        constraints = [
            models.UniqueConstraint(
                fields=['solicitante', 'objeto'],
                name='unique_solicitante_objeto',
            ),
        ]

    def __str__(self):
        return f'Solicitação #{self.pk} - {self.objeto.titulo} ({self.get_status_display()})'
