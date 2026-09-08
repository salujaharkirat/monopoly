"""
Ensures every User has a Player profile.

Previously only LoginView created one (via get_or_create), which meant a
freshly registered user got a 500 on `request.user.monopoly_player` the moment
they hit any game endpoint before their first login. Creating it here, once,
on User creation, means there is a single place this happens instead of every
view needing its own get_or_create.
"""

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from game.models import Player


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_player_for_new_user(sender, instance, created, **kwargs):
  if not created:
    return

  Player.objects.get_or_create(
    user=instance,
    defaults={
      'money': 2000,
      'position': 0,
      'is_in_jail': False,
      'is_active': True,
    }
  )
