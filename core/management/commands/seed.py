"""
Comando de management para popular o banco com dados iniciais.

Cria categorias, locais e um usuário admin padrão.
Uso: python manage.py seed
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import Categoria, Local, Perfil

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Popula o banco de dados com categorias, locais e usuário admin padrão.'

    def handle(self, *args, **options):
        self.stdout.write('Criando dados iniciais...')

        categorias = [
            ('Eletrônicos', 'Celulares, notebooks, tablets, fones de ouvido, carregadores, etc.'),
            ('Documentos', 'Carteira de identidade, carteirinha, CNH, passaporte, etc.'),
            ('Vestuário', 'Roupas, calçados, bonés, jaquetas, etc.'),
            ('Acessórios', 'Bolsas, mochilas, óculos, relógios, bijuterias, etc.'),
            ('Chaves', 'Chaves de casa, carro, cadeado, etc.'),
            ('Material Escolar', 'Cadernos, livros, estojos, calculadoras, etc.'),
            ('Garrafas e Copos', 'Garrafas de água, copos térmicos, squeeze, etc.'),
            ('Outros', 'Objetos que não se enquadram nas categorias acima.'),
        ]
        for nome, descricao in categorias:
            Categoria.objects.get_or_create(nome=nome, defaults={'descricao': descricao})
        self.stdout.write(self.style.SUCCESS(f'  {len(categorias)} categorias criadas/verificadas.'))

        locais = [
            ('Biblioteca do Leme', 'Prédio Leme', '7º andar', 'Biblioteca do Leme'),
            ('Biblioteca do Frigs', 'Prédio Frigs', '2º andar', 'Biblioteca do Frigs'),
            ('Bandejao', '', '', 'Bandejao'),
            ('LABGRAD', 'LABGRAD', '', 'Lab de graduação para informática'),
            ('Quadra Esportiva', '', '', 'Quadra poliesportiva'),
            ('Estacionamento', '', '', 'Estacionamento dos alunos'),
        ]
        for nome, predio, andar, descricao in locais:
            Local.objects.get_or_create(
                nome=nome,
                predio=predio,
                defaults={'andar': andar, 'descricao': descricao},
            )
        self.stdout.write(self.style.SUCCESS(f'  {len(locais)} locais criados/verificados.'))

        usuario_admin, usuario_criado = Usuario.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Administrador',
                'last_name': 'PUC Encontra',
                'email': 'admin@puc.br',
                'is_staff': True,
                'is_superuser': True,
            },
        )

        campos_alterados = []
        if not usuario_admin.is_staff:
            usuario_admin.is_staff = True
            campos_alterados.append('is_staff')
        if not usuario_admin.is_superuser:
            usuario_admin.is_superuser = True
            campos_alterados.append('is_superuser')
        if campos_alterados:
            usuario_admin.save(update_fields=campos_alterados)

        if usuario_criado:
            usuario_admin.set_password('admin123')
            usuario_admin.save(update_fields=['password'])
            self.stdout.write(self.style.SUCCESS('  Usuário admin criado (login: admin / senha: admin123)'))
        else:
            self.stdout.write('  Usuário admin já existe.')

        Perfil.objects.update_or_create(
            user=usuario_admin,
            defaults={'tipo': 'admin', 'matricula': '000000', 'telefone': '00000000000'},
        )

        self.stdout.write(self.style.SUCCESS('Dados iniciais criados com sucesso!'))
