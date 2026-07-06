import logging

from django.core.exceptions import ValidationError

from .models import Game, Player

logger = logging(__name__)

class GameService:
  @staticmethod
  def start_game(game_id, player_id):
    try:
      game = Game.objects.get(id=game_id)
      player = Player.objects.get(id=player_id)

      if player != game.created_by:
        return {
          'success': False,
          'message': 'Only creator can start the game'
        }
      
      can_start, errors = game.can_start(player)

      if not can_start:
        return {
          'success': False,
          'message': '\n'.join(errors)
        }

      game.start_game(player)

      game_state = GameService.get_game_state(game_id)
      return {
        'success': True,
        'message': 'Game started successfully',
        'game_state': game_state
      }
    except Game.DoesNotExist:
      return {'success': False, 'message': 'Game not found'}
    except Player.DoesNotExist:
      return {'success': False, 'message': 'Player not found'}
    except ValidationError as e:
        return {'success': False, 'message': str(e)}
    except Exception as e:
        logger.error(f"Error starting game: {e}")
        return {'success': False, 'message': 'An error occurred'}

  @staticmethod
  def get_game_state(game_id):
    """Get current game state as dictionary"""
    try:
      game = Game.objects.prefetch_related('players').get(id=game_id)
      
      return {
        'id': game.id,
        'name': game.name,
        'state': game.state,
        'current_player_index': game.current_player_index,
        'number_of_turns': game.number_of_turns,
        'players': [
            {
              'id': player.id,
              'username': player.user.username,
              'money': player.money,
              'position': player.position,
              'is_in_jail': player.is_in_jail,
              'is_active': player.is_active
            }
            for player in game.players.all()
        ],
        'player_count': game.players.count(),
        'max_players': game.max_players,
        'min_players': game.min_players,
        'created_by': game.created_by.user.username,
        'created_at': game.created_at.isoformat(),
        'updated_at': game.updated_at.isoformat()
      }
    except Game.DoesNotExist:
        return None

  @staticmethod
  def roll_dice(game_id, player_id):
    """Roll dice and handle turn"""
    # Implementation for Phase 3
    pass
  
  @staticmethod
  def buy_property(game_id, player_id, property_id):
    """Buy a property"""
    # Implementation for Phase 3
    pass
  
  @staticmethod
  def end_turn(game_id, player_id):
    """End current turn"""
    # Implementation for Phase 3
    pass

  