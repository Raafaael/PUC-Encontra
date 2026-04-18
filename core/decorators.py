from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .access import usuario_tem_papel


def papel_obrigatorio(*papeis):
    def decorador(funcao_view):
        @wraps(funcao_view)
        def encapsular(requisicao, *args, **kwargs):
            if not requisicao.user.is_authenticated:
                return redirect('login')
            if usuario_tem_papel(requisicao.user, *papeis):
                return funcao_view(requisicao, *args, **kwargs)
            messages.error(requisicao, 'Você não tem permissão para acessar esta página.')
            return redirect('dashboard')

        return encapsular

    return decorador
