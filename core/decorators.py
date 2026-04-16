from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .access import user_has_role


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if user_has_role(request.user, *roles):
                return view_func(request, *args, **kwargs)
            messages.error(request, 'Você não tem permissão para acessar esta página.')
            return redirect('dashboard')

        return wrapper

    return decorator
