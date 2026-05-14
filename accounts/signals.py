"""Accounts signals — User oluştuğunda otomatik Profile yaratır."""
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Yeni User kaydı oluşunca otomatik olarak Profile yarat."""
    if created:
        Profile.objects.create(user=instance)
