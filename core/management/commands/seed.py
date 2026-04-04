"""
Comando de management para popular o banco com dados iniciais.

Cria categorias, locais e um usuário admin padrão.
Uso: python manage.py seed
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import Categoria, Local, Perfil


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
        for nome, desc in categorias:
            Categoria.objects.get_or_create(nome=nome, defaults={'descricao': desc})
        self.stdout.write(self.style.SUCCESS(f'  {len(categorias)} categorias criadas/verificadas.'))

        locais = [
            ('Biblioteca do Leme', 'Prédio Leme', '7º andar', 'Biblioteca do Leme'),
            ('Biblioteca do Frigs', 'Prédio Frigs', '2º andar', 'Biblioteca do Frigs'),
            ('Bandejao', '', '', 'Bandejao'),
            ('LABGRAD', 'LABGRAD', '', 'Lab de graduação para informática'),
            ('Quadra Esportiva', '', '', 'Quadra poliesportiva'),
            ('Estacionamento', '', '', 'Estacionamento dos alunos'),
        ]
        for nome, predio, andar, desc in locais:
            Local.objects.get_or_create(
                nome=nome,
                predio=predio,
                defaults={'andar': andar, 'descricao': desc},
            )
        self.stdout.write(self.style.SUCCESS(f'  {len(locais)} locais criados/verificados.'))

        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Administrador',
                'last_name': 'PUC Encontra',
                'email': 'admin@puc.br',
                'is_staff': True,
                'is_superuser': True,
            },
        )

        changed_fields = []
        if not admin_user.is_staff:
            admin_user.is_staff = True
            changed_fields.append('is_staff')
        if not admin_user.is_superuser:
            admin_user.is_superuser = True
            changed_fields.append('is_superuser')
        if changed_fields:
            admin_user.save(update_fields=changed_fields)

        if created:
            admin_user.set_password('admin123')
            admin_user.save(update_fields=['password'])
            self.stdout.write(self.style.SUCCESS('  Usuário admin criado (login: admin / senha: admin123)'))
        else:
            self.stdout.write('  Usuário admin já existe.')

        Perfil.objects.update_or_create(
            user=admin_user,
            defaults={'tipo': 'admin', 'matricula': '000000', 'telefone': '00000000000'},
        )

        self.stdout.write(self.style.SUCCESS('Dados iniciais criados com sucesso!'))
