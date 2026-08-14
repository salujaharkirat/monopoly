from models import Player, Game
from channels.db import database_sync_to_async
from serializer import GameDetailSerializer

class DbUtils:
  @database_sync_to_async
  @staticmethod
  def get_player(user):
    return Player.objects.get(user=user)

  @database_sync_to_async
  @staticmethod
  def get_game(game_id) -> Game | None:
    """Get game with related fields prefetched"""
    try:
      game = Game.objects.select_related('created_by', 'created_by__user').get(id=game_id)
      return game
    except Game.DoesNotExist:
      return None

  @database_sync_to_async
  @staticmethod
  def start_game(game: Game):
    game.start_game()
    game.save()
    return game

  @database_sync_to_async
  @staticmethod
  def get_game_state(game_id):
    game = Game.objects.get(id=game_id)
    return GameDetailSerializer(game).data

  @database_sync_to_async
  @staticmethod
  def can_start_game(game, player):
    return game.can_start(player)
