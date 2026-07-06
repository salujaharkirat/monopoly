from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
  user = models.OneToOneField(
      User, 
      on_delete=models.PROTECT,
      related_name='monopoly_player'
  )
  money = models.IntegerField(default=2000)
  position = models.IntegerField(default=0)
  is_in_jail = models.BooleanField(default=False)
  is_active = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

class Game(models.Model):
  GAME_STATE_CHOICES = [
      ("N", "NOT STARTED"),
      ("P", "PLAYING"),
      ("F", "FINISHED"),
  ]
  name = models.CharField(max_length=100, default="Monopoly Game")
  players = models.ManyToManyField(
    Player,
    related_name="games",
    verbose_name="list of players"
  )
  state = models.CharField(max_length=1, choices=GAME_STATE_CHOICES, default="N")
  current_player_index = models.IntegerField(default=0)
  number_of_turns = models.IntegerField(default=0)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
