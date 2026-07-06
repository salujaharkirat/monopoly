import logging
import random

from django.core.exceptions import ValidationError

from .models import Game, Player, Square
from .serializer import GameDetailSerializer

logger = logging.getLogger(__name__)

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
        'turn_number': game.turn_number,
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
    try:
      game = Game.objects.select_related('created_by').prefetch_related('players').get(id=game_id)
      player = Player.objects.get(id=player_id)



      if game.state != Game.GameState.PLAYING:
        return {
          'success': False,
          'message': 'Game is not in playing state'
        }
      
      current_player = game.get_current_player()
      if current_player.id != player.id:
        return {
          'success': False,
          'message': 'Not your turn'          
        }
      
      if player.is_in_jail:
        return {
          'success': False,
          'message': 'Player is in jail. Pay $50 or use get out of jail card'
        }
      

      dice1 = random.randint(1, 6)
      dice2 = random.randint(1, 6)
      total = dice1 + dice2
      is_doubles = dice1 == dice2

      # Calculate new position
      old_position = player.position
      new_position = (old_position + total) % 40


      # Check if passed GO    
      passed_go = new_position < old_position

      # Upate player position
      player.position = new_position
      player.save()

      if passed_go:
        player.money += 200
        player.save()
    

      
      square = Square.objects.get(position=new_position)
      square_result = GameService.handle_square_landing(player, square, game)

      if player.money < 0:
        return {
          'success': False,
          'message': 'Player is bankrupt',
          'bankrupt': True
        }
      
      if not is_doubles:
        game.next_turn()
        game.save()
      
      game_state = GameDetailSerializer(game).data


      return {
        'success': True,
        'data': {
          'dice': {
            'dice1': dice1,
            'dice2': dice2,
            'is_doubles': is_doubles,
            'old_position': old_position,
            'new_position': new_position,
            'passed_go': passed_go
          },
          'square_result': square_result,
          'game_state': game_state
        }
      }
    except Game.DoesNotExist:
      return {'success': False, 'message': 'Game not found'}
    except Player.DoesNotExist:
      return {'success': False, 'message': 'Player not found'}
    except Exception as e:
      return {'success': False, 'message': str(e)}
  
  @staticmethod
  def handle_square_landing(player, square, game):
    result = {
      'square': square.position,
      'name': square.name,
      'type': square.square_type,
      'message': ''
    }

    if square.square_type == Square.SquareType.GO:
      result['message'] = f"{player.user.username} collected $200"
    elif square.square_type == Square.SquareType.PROPERTY:
      try:
        property_obj = square.property
        if property_obj.owner:
          if property_obj.owner.id != player.id:
            rent = square.rent or 0
            player.money -= rent
            property_obj.owner.money += rent
            player.save()
            property_obj.owner.save()
            result['message'] = f"Paid ${rent} rent to {property_obj.owner.user.username}"
          else:
            result['message'] = f"Owned by {player.user.username}"
        else:
          result['message'] = f"Property available for ${square.price}"
          result['can_buy'] = True
          result['price'] = square.price
      except:
        result['message'] = 'Property not available'
    elif square.square_type == Square.SquareType.TAX:
      tax_amount = square.tax_amount or 100
      player.money -= tax_amount
      player.save()
      result['message'] = f"Paid ${tax_amount} in taxes"
    elif square.square_type == Square.SquareType.GO_TO_JAIL:
      player.position = 10
      player.is_in_jail = True
      player.save()
      result['message'] = "Go to Jail!"
      pass
    elif square.square_type == Square.SquareType.CHANCE:
      result['message'] = "Chance card drawn"
      # TODO: Will implement later
    elif square.square_type == Square.SquareType.COMMUNITY_CHEST:
      result['message'] = "Community Chest card drawn"
      # Will implement later
    elif square.square_type in [Square.SquareType.RAILROAD, Square.SquareType.UTILITY]:
      result['message'] = f"Landed on {square.name}"
      # Will implement later

    return result

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

  