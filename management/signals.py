from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
  if created:
    # По умолчанию делаем нового пользователя учеником, если не указано иное
    Profile.objects.create(user=instance, role='student')


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
  if hasattr(instance, 'profile'):
    instance.profile.save()