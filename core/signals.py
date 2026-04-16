from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Perfil

User = get_user_model()


@receiver(post_save, sender=User)
def ensure_user_profile(sender, instance, **kwargs):
    perfil, _ = Perfil.objects.get_or_create(
        user=instance,
        defaults={'tipo': 'admin' if instance.is_superuser else 'usuario'},
    )

    if instance.is_superuser and perfil.tipo != 'admin':
        perfil.tipo = 'admin'
        perfil.save(update_fields=['tipo'])
    elif perfil.tipo == 'aluno':
        perfil.tipo = 'usuario'
        perfil.save(update_fields=['tipo'])
