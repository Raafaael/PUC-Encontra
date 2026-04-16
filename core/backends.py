from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailOuUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        credential = username or kwargs.get(User.USERNAME_FIELD) or kwargs.get('email')
        if not credential or password is None:
            return None

        user = User.objects.filter(username=credential).first()
        if user is None:
            email_matches = User.objects.filter(email__iexact=credential).order_by('pk')
            if email_matches.count() != 1:
                return None
            user = email_matches.first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
