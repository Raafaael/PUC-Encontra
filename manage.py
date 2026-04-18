"""Utilitário de linha de comando do Django para tarefas administrativas."""
import os
import sys


def principal():
    """Executa tarefas administrativas."""
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        os.environ.get(
            'DJANGO_SETTINGS_MODULE', 'puc_encontra.settings.development'
        ),
    )
    try:
        from django.core.management import execute_from_command_line
    except ImportError as erro_importacao:
        raise ImportError(
            "Não foi possível importar o Django. Verifique se está instalado "
            "e disponível na variável de ambiente PYTHONPATH. Você ativou o "
            "ambiente virtual?"
        ) from erro_importacao
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    principal()
