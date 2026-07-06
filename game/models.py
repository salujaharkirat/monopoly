from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

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
  class GameState(models.TextChoices):
    WAITING = 'WT', 'Waiting for Players'
    PLAYING = 'PL', 'Playing'
    FINISHED = 'FI', 'Finished'
    CANCELLED = 'CA', 'Cancelled'

  name = models.CharField(max_length=100, default="Monopoly Game")
  players = models.ManyToManyField(
    Player,
    related_name="games",
    verbose_name="list of players"
  )
  max_players = models.IntegerField(
      default=4,
      validators=[MinValueValidator(2), MaxValueValidator(8)]
  )
  min_players = models.IntegerField(
      default=2,
      validators=[MinValueValidator(2), MaxValueValidator(4)]
  )
  state = models.CharField(max_length=2, choices=GameState.choices,
        default=GameState.WAITING)
  current_player_index = models.IntegerField(default=0)
  turn_number = models.IntegerField(default=0)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  created_by = models.ForeignKey(Player,  on_delete=models.PROTECT, related_name='created_games',         null=True,  # Allow null temporarily
        blank=True)  # Allow blank in forms)

  def can_join(self, player):
    """Check if a player can join this game"""
    if self.state != self.GameState.WAITING:
        return False, "Game already started or finished"
    if self.players.count() >= self.max_players:
        return False, "Game is full"
    if self.players.filter(id=player.id).exists():
        return False, "Already in this game"
    if not player.is_active:
        return False, "Player is inactive"
    return True, "Can join"
  
  def can_start(self):
     pass
  
  def start_game(self):
    can_start, errors = self.can_start()
    if not can_start:
        raise ValidationError("\n".join(errors))
    
    self.state = self.GameState.PLAYING
    self.current_player_index = 0
    self.number_of_turns = 0

    for player in self.players.all():
        player.money = 2000
        player.position = 0
        player.is_in_jail = False
        player.save()
    
    self.save()

    return self

  def get_current_player(self):
    """Get current player"""
    players = list(self.players.all())
    if not players:
        return None
    return players[self.current_player_index]
  
  def next_turn(self):
    if self.state != self.GameState.PLAYING:
        raise ValidationError("Game is not in playing state")

    player_count = self.players.count()
    self.current_player_index = (self.current_player_index + 1) % player_count
    self.number_of_turns += 1
    self.save()

    return self.get_current_player()

     