from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

Usuario = get_user_model()


class EmailOuUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        credencial = username or kwargs.get(Usuario.USERNAME_FIELD) or kwargs.get('email')
        if not credencial or password is None:
            return None

        usuario = Usuario.objects.filter(username=credencial).first()
        if usuario is None:
            correspondencias_email = Usuario.objects.filter(email__iexact=credencial).order_by('pk')
            if correspondencias_email.count() != 1:
                return None
            usuario = correspondencias_email.first()

        if usuario and usuario.check_password(password) and self.user_can_authenticate(usuario):
            return usuario
        return None
