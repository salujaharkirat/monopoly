import logging
import random

from django.core.exceptions import ValidationError
from game.strategies.square_strategy import SquareStrategyFactory

from .models import Game, Player, Square, Property
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
      
      game.start_game()

      for square in Square.objects.all():
        Property.objects.create(
            square=square,
            game=game,
            owner=None,  # ✅ Empty! Unowned
            houses=0,
            is_mortgaged=False
        )

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
      if not current_player:
        return {
          'success': False,
          'message': 'Player not found'
        }
      
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

      # Update player position
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
            'passed_go': passed_go,
            'total': total,
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

    strategy = SquareStrategyFactory.get_strategy(square.type)
    strategy_result = strategy.execute(player, square, game)

    return result

  @staticmethod
  def buy_property(game_id, player_id, property_id):
    """Buy a property"""
    try:
      game = Game.objects.get(id=game_id)
      player = Player.objects.get(id=player_id)

      if not game or not player:
        return {
            'success': False,
            'message': 'Game or Player not found'
        }

      # Validate
      if game.state != Game.GameState.PLAYING:
        return {
            'success': False,
            'message': 'Game is not in playing state'
        }
      

      property_obj = Property.objects.select_related('square', 'owner').get(id=property_id, game=game)
  
      if property_obj.owner:
        return {
          'success': False,
          'message': 'Property is already owned'
        }

      if not property_obj.square:
        return {
          'success': False,
          'message': 'No square mapping found for property'
        }

      # Check if this square can be purchased
      if property_obj.square.square_type not in [
          Square.SquareType.PROPERTY,
          Square.SquareType.RAILROAD,
          Square.SquareType.UTILITY
      ]:
        return {
            'success': False,
            'message': f'{property_obj.square.name} cannot be purchased'
        }
      
      price = property_obj.square.price
      if price is None:
        return {
          'success': False,
          'message': f'{property_obj.square.name} doesn ot have a valid price'
        }

      if player.money < price:
        return {
          'success': False,
          'message': f'Not enough money! Need ${property_obj.square.price}, have ${player.money}'
        }
      
      current_player = game.get_current_player()
  
      if current_player is None:
        return {
            'success': False,
            'message': 'No current player found'
        }

      if current_player.id != player.id:
        return {
          'success': False,
          'message': 'Not your turn'
        }
  
      # Check if player is on this property
      if player.position != property_obj.square.position:
        return {
            'success': False,
            'message': 'You are not on this property'
        }
      
      player.money -= price
      property_obj.set_owner(player)
      property_obj.save()
      player.save()

      return {
        'success': True,
        'message': f'{player.user.username} bought {property_obj.square.name} for ${property_obj.square.price}',
        'data': {
          'property_id': property_obj.id,
          'property_name': property_obj.square.name,
          'price': property_obj.square.price,
          'player_money': player.money
        }
      }

    except Game.DoesNotExist:
      return {'success': False, 'message': 'Game not found'}
    except Player.DoesNotExist:
      return {'success': False, 'message': 'Player not found'}
    except Property.DoesNotExist:
      return {'success': False, 'message': 'Property not found'}
    except Exception as e:
      return {'success': False, 'message': str(e)}
  
  @staticmethod
  def end_turn(game_id):
    """End current turn"""
    try:
      game = Game.objects.select_related('created_by').prefetch_related('players').get(id=game_id)
      total_players = game.players.count()
      next_player_index = (game.current_player_index + 1) % total_players
      game.turn_number += 1
      game.current_player_index = next_player_index
      game.save()

      next_player = game.get_current_player()

      return {
        'success': True,
        'message': f"{next_player.user.username}'s turn now"
      }
    except Exception as e:
      return {'success': False, 'message': str(e)}

  @staticmethod
  def leave_game(game_id, player_id):
    try:
      game = Game.objects.select_related('created_by').prefetch_related('players').get(id=game_id)
      player = Player.objects.get(id=player_id)

      if not game.players.filter(id=player.id).exists():
        return {
          'success': False,
          'message': 'You are not in this game'
        }
      
      if game.state == Game.GameState.FINISHED:
        return {
          'success': False,
          'message': 'Game is already finished'
        }
      
      if game.state == Game.GameState.PLAYING:
        properties = Property.objects.filter(owner=player, game=game)
        for prop in properties:
          prop.owner = None
          prop.houses = 0
          prop.is_mortgaged = False
          prop.save()
      
      game.players.remove(player)
      if game.created_by.id == player_id and game.players.exists():
        new_creator = game.players.first()
        game.created_by = new_creator
        game.save()
      
      if game.state == Game.GameState.WAITING:
        if game.players.count() == 0:
          Property.objects.filter(game=game).delete()
          game.delete()
          return {
            'success': True,
            'message': f'Game {game.name} was not started and empty and is deleted',
            'game_deleted': True
          }
        if game.players.count() < game.min_players:
          pass
      
      if game.state == Game.GameState.PLAYING and game.players.count() < 2:
        game.state = Game.GameState.FINISHED
        game.save()

        winner = game.players.first()
        return {
          'success': True,
          'message': f'{player.user.username} left the game. {winner.user.username} wins!',
          'game_ended': True,
          'winner': winner.user.username
                              
        }
      
      game.save()
      return {
        'success': True,
        'message': f'{player.user.username} left the game',
        'game_id': game.id,
        'player_count': game.players.count(),
        'game_state': game.state
      }
    except Game.DoesNotExist:
      return {'success': False, 'message': 'Game not found'}
    except Player.DoesNotExist:
      return {'success': False, 'message': 'Player not found'}
    except Exception as e:
      return {'success': False, 'message': str(e)}

  