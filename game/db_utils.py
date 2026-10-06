import logging

from game.models import Player, Game
from channels.db import database_sync_to_async
from game.serializer import GameDetailSerializer
from rest_framework.authtoken.models import Token

logger = logging.getLogger(__name__)


class DbUtils:
  @staticmethod
  @database_sync_to_async
  def get_token(key):
      try:
        return Token.objects.get(key=key)
      except Token.DoesNotExist:
        return None

  @staticmethod
  @database_sync_to_async
  def get_user_from_token(key):
      """Get user from token - handles all cases"""
      try:
          token = Token.objects.select_related('user').get(key=key)

          user = getattr(token, 'user', None)

          if not user:
              logger.warning("Token has no user")
              return None

          return user

      except Token.DoesNotExist:
          logger.warning(f"Token not found: {key[:20]}...")
          return None
      except Exception:
          logger.exception("Error getting user from token")
          return None

  @staticmethod
  @database_sync_to_async
  def get_player(user):
    try:
      return Player.objects.get(user=user)
    except Player.DoesNotExist:
      return None

  @staticmethod
  @database_sync_to_async
  def get_game(game_id) -> Game | None:
    """Get game with related fields prefetched"""
    try:
      game = Game.objects.select_related('created_by', 'created_by__user').get(id=game_id)
      return game
    except Game.DoesNotExist:
      return None

  @staticmethod
  @database_sync_to_async
  def get_game_state(game_id):
    game = Game.objects.get(id=game_id)
    return GameDetailSerializer(game).data

  @staticmethod
  @database_sync_to_async
  def is_player_in_game(player, game):
    return game.players.filter(id=player.id).exists()
