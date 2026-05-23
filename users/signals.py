from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Consulta


@receiver(post_save, sender=Consulta)
def signals_gravacoes_transcricao_resumos(sender, instance, created, **kwargs):
    if created:
        pass
