import logging
import random

from django.core.exceptions import ValidationError

from game.constants import COMMUNITY_CHEST_CARDS
from game.enums import CardType

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
        # game.next_turn()
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
      community_card_result = GameService.handle_community_card(player, game)
      if community_card_result['success']:
        result['card'] = community_card_result
        result['message'] = f"📬 {community_card_result['card_name']}: {community_card_result['description']}"
        if community_card_result.get('amount'):
            result['message'] += f" (${community_card_result['amount']})"
      else:
        result['message'] = f"📬 Community Chest: {community_card_result['message']}"
    elif square.square_type in [Square.SquareType.RAILROAD, Square.SquareType.UTILITY]:
      result['message'] = f"Landed on {square.name}"
      # Will implement later

    return result

  @staticmethod
  def handle_community_card(player, game):
    card = random.choice(COMMUNITY_CHEST_CARDS)
    result = GameService.process_community_card(player, game, card)

    return {
      'success': True,
      'card_name': card['name'],
      'description': card['description'],
      'type': card['type'],
      'amount': result.get('amount', 0),
      'message': result.get('message', ''),
      'card': card
    }

  @staticmethod
  def process_community_card(player,game, card):
    type = card.get('type')
    amount = card.get('amount', 0)
    result = {'amount': 0, 'message': ''}

    if type == CardType.COLLECT_MONEY:
      player.money += amount
      player.save()
      result['amount'] = player.money
      result['message'] = f"Collected ${amount}"
    elif type == CardType.PAY_MONEY:
      if player.money < amount:
        return {
            'amount': 0,
            'message': f"Not enough money to pay ${amount}"
        }
      player.money -= amount
      player.save()
      result['amount'] = player.money
      result['message'] = f"Paid ${amount}"
    elif type == CardType.ADVANCE_TO_GO:
      player.position = 0
      player.money += 200
      player.save()
      result['amount'] = 200
      result['message'] = "Advanced to GO and collected $200"
    elif type == CardType.GO_TO_JAIL:
      player.position = 10
      player.is_in_jail = True
      player.save()
      result['message'] = "Go to Jail!"
    elif type == CardType.COLLECT_FROM_ALL:
      total_collected = 0
      for p in game.players.all():
        if p.id != player.id:
          if p.money >= amount:
            p.money -= amount
            total_collected += amount
            p.save()
          else:
            total_collected += p.money
            p.money = 0
            p.save()

      player.money += total_collected
      player.save()
      result['amount'] = total_collected
      result['message'] = f'Collected ${total_collected} from other players'

    elif type == CardType.STREET_REPAIRS:
      total_cost = 0
      for property in player.properties.all():
        total_cost += property.houses * 40 + property.hotels * 115

      if player.money < total_cost:
        return {
          'amount': 0,
          'message': f"Not enough money for street repairs (${total_cost})"
        }

      player.money -= total_cost
      player.save()
      result['amount'] = total_cost
      result['message'] = f"Paid ${total_cost} for street repairs"

    print("here...", result)
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

  