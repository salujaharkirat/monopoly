from models import Player, Game
from channels.db import database_sync_to_async
from serializer import GameDetailSerializer
from rest_framework.authtoken.models import Token
class DbUtils:
  @database_sync_to_async
  @staticmethod
  def get_token(key):
      try:
          return Token.objects.get(key=key)
      except Token.DoesNotExist:
          return None

  @database_sync_to_async
  @staticmethod
  def get_user_from_token(key):
      """Get user from token - handles all cases"""
      try:
          token = Token.objects.select_related('user').get(key=key)
          
          user = getattr(token, 'user', None)
          
          if not user:
              print("Token has no user")
              return None
              
          return user
          
      except Token.DoesNotExist:
          print(f"Token not found: {key[:20]}...")
          return None
      except Exception as e:
          print(f"Error getting user: {type(e).__name__}: {e}")
          import traceback
          traceback.print_exc()
          return None
  
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

  @database_sync_to_async
  @staticmethod
  def is_player_in_game(player, game):
    return game.players.filter(id=player.id).exists()
