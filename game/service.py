import functools
import logging
import random

from game import turn_order
from game.enums import SquareType
from game.strategies.square_strategy import SquareStrategyFactory

from .exceptions import (
  BuildRuleViolation,
  GameError,
  GameNotFound,
  InsufficientFunds,
  InvalidAction,
  InvalidGameState,
  NotAuthorized,
  NotPropertyOwner,
  NotYourTurn,
  PlayerBankrupt,
  PlayerInJail,
  PlayerNotFound,
  PropertyAlreadyOwned,
  PropertyNotFound,
  PropertyNotPurchasable,
  SquareNotFound,
)
from .models import Game, Player, Square, Property
from .serializer import GameDetailSerializer

logger = logging.getLogger(__name__)


def service_result(func):
  """Convert `GameError` into the ``{'success': False}`` response shape.

  Only `GameError` is caught. Every other exception is a bug and propagates to
  the caller, so it surfaces as a traceback instead of being handed to the
  player as if it were a rule violation.
  """
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except GameError as exc:
      logger.info(f"{func.__name__} refused: {exc}")
      return {
        'success': False,
        'message': str(exc),
        'error': type(exc).__name__,
        **exc.payload,
      }
  return wrapper


def _get_game(game_id):
  try:
    return Game.objects.get(id=game_id)
  except Game.DoesNotExist:
    raise GameNotFound('Game not found')


def _get_player(player_id):
  try:
    return Player.objects.get(id=player_id)
  except Player.DoesNotExist:
    raise PlayerNotFound('Player not found')


class GameService:
  @staticmethod
  @service_result
  def start_game(game_id, player_id):
    game = _get_game(game_id)
    player = _get_player(player_id)

    if player != game.created_by:
      raise NotAuthorized('Only creator can start the game')

    can_start, error_message = game.can_start(player)
    if not can_start:
      raise InvalidGameState(error_message)

    game.start_game()

    for square in Square.objects.all():
      Property.objects.create(
          square=square,
          game=game,
          owner=None,
          houses=0,
          is_mortgaged=False
      )

    return {
      'success': True,
      'message': 'Game started successfully',
      'game_state': GameService.get_game_state(game_id)
    }

  @staticmethod
  @service_result
  def get_game_state(game_id):
    """Get current game state as dictionary.

    Raises `GameNotFound` rather than returning None, so a missing game can
    never be mistaken for an empty one.
    """
    try:
      game = Game.objects.prefetch_related('players').get(id=game_id)
    except Game.DoesNotExist:
      raise GameNotFound('Game not found')

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

  @staticmethod
  @service_result
  def roll_dice(game_id, player_id):
    try:
      game = Game.objects.select_related('created_by').prefetch_related('players').get(id=game_id)
    except Game.DoesNotExist:
      raise GameNotFound('Game not found')
    player = _get_player(player_id)

    if game.state != Game.GameState.PLAYING:
      raise InvalidGameState('Game is not in playing state')

    current_player = turn_order.get_current_player(game)
    if not current_player:
      raise PlayerNotFound('Player not found')

    if current_player.id != player.id:
      raise NotYourTurn('Not your turn')

    if player.is_in_jail:
      raise PlayerInJail('Player is in jail. Pay $50 or use get out of jail card')

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

    try:
      square = Square.objects.get(position=new_position)
    except Square.DoesNotExist:
      raise SquareNotFound(f'No square configured at position {new_position}')

    square_result = GameService.handle_square_landing(player, square, game, total)

    if player.money < 0:
      raise PlayerBankrupt('Player is bankrupt', bankrupt=True)

    if not is_doubles:
      turn_order.advance_turn(game)

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
        'game_state': GameDetailSerializer(game).data
      }
    }

  @staticmethod
  def handle_square_landing(player, square, game, dice_roll=0):
    result = {
      'square': square.position,
      'name': square.name,
      'type': square.square_type,
      'message': ''
    }

    strategy = SquareStrategyFactory.get_strategy(square.square_type)
    # dice_roll is needed for utility rent, which is a multiple of the roll.
    strategy_result = strategy.execute(player, square, game, dice_roll)

    return {**result, **strategy_result}

  @staticmethod
  @service_result
  def buy_property(game_id, player_id, property_id):
    """Buy a property"""
    game = _get_game(game_id)
    player = _get_player(player_id)

    if game.state != Game.GameState.PLAYING:
      raise InvalidGameState('Game is not in playing state')

    try:
      property_obj = Property.objects.select_related('square', 'owner').get(id=property_id, game=game)
    except Property.DoesNotExist:
      raise PropertyNotFound('Property not found')

    if property_obj.owner:
      raise PropertyAlreadyOwned('Property is already owned')

    if not property_obj.square:
      raise PropertyNotPurchasable('No square mapping found for property')

    # Check if this square can be purchased
    if property_obj.square.square_type not in [
        SquareType.PROPERTY,
        SquareType.RAIL_ROAD,
        SquareType.UTILITY
    ]:
      raise PropertyNotPurchasable(f'{property_obj.square.name} cannot be purchased')

    price = property_obj.square.price
    if price is None:
      raise PropertyNotPurchasable(f'{property_obj.square.name} does not have a valid price')

    if player.money < price:
      raise InsufficientFunds(
        f'Not enough money! Need ${price}, have ${player.money}'
      )

    current_player = turn_order.get_current_player(game)
    if current_player is None:
      raise PlayerNotFound('No current player found')

    if current_player.id != player.id:
      raise NotYourTurn('Not your turn')

    # Check if player is on this property
    if player.position != property_obj.square.position:
      raise InvalidAction('You are not on this property')

    player.money -= price
    property_obj.set_owner(player)
    property_obj.save()
    player.save()

    return {
      'success': True,
      'message': f'{player.user.username} bought {property_obj.square.name} for ${price}',
      'data': {
        'property_id': property_obj.id,
        'property_name': property_obj.square.name,
        'price': price,
        'player_money': player.money
      }
    }

  @staticmethod
  @service_result
  def end_turn(game_id):
    """End current turn"""
    try:
      game = Game.objects.select_related('created_by').prefetch_related('players').get(id=game_id)
    except Game.DoesNotExist:
      raise GameNotFound('Game not found')

    if game.players.count() == 0:
      raise InvalidGameState('Game has no players')

    next_player = turn_order.advance_turn(game)

    return {
      'success': True,
      'message': f"{next_player.user.username}'s turn now"
    }

  @staticmethod
  @service_result
  def build_house(game_id, player_id, property_id, number_of_houses):
    player = _get_player(player_id)
    game = _get_game(game_id)
    try:
      property = Property.objects.select_related('square', 'owner', 'square__color_group').get(id=property_id, game=game)
    except Property.DoesNotExist:
      raise PropertyNotFound('Property not found')

    if property.square and property.square.square_type != SquareType.PROPERTY:
      raise BuildRuleViolation(f"Cannot build on {property.square.name} (not a property)")


    if number_of_houses < 1 or number_of_houses > 5:
      raise InvalidAction("number_of_houses must be between 1 and 5")

    if property.owner is None or property.owner.id != player.id:
      raise NotPropertyOwner(
        f"Player {player.user.username} does not own {property.square.name}"
      )

    color_group = property.square.color_group
    if color_group is None:
      raise BuildRuleViolation(
        f"{property.square.name} has no color group configured, so build rules cannot be checked"
      )

    owned_in_group = Property.objects.filter(
        owner=player,
        square__color_group=color_group,
        game=game
    ).count()
    total_in_group = Property.objects.filter(
        square__color_group=color_group,
        game=game
    ).count()

    if total_in_group != owned_in_group:
      raise BuildRuleViolation(
        f"Must own all {color_group.name} properties to build on {property.square.name}"
      )

    if property.houses + number_of_houses > 5:
      raise BuildRuleViolation(
        f"Cannot have more than 5 houses/1 hotel on {property.square.name} (current: {property.houses})"
      )

    # Legality before affordability, so an illegal build reports the rule it
    # breaks rather than complaining about money.
    allowed, reason = GameService.can_evenly_construct(
      color_group, game, property, number_of_houses
    )
    if not allowed:
      raise BuildRuleViolation(reason)

    if property.square.house_cost is None:
      # Board misconfiguration, not something the player did. Loud on purpose,
      # but legible rather than a bare TypeError on `None * n`.
      raise ValueError(
        f"Square {property.square.position} ({property.square.name}) has no "
        f"house_cost; re-run `manage.py init_board` to backfill it"
      )

    construction_cost = property.square.house_cost * number_of_houses

    if player.money < construction_cost:
      raise InsufficientFunds(
        f"Player {player.user.username} does not have ${construction_cost} to make {number_of_houses} houses"
      )

    player.money -= construction_cost
    property.houses += number_of_houses
    player.save()
    property.save()

    return {
      'success': True,
      'message': f"Player {player.user.username} constructed {number_of_houses} on property {property.square.name}",
      'data': {
        'property_id': property.id,
        'property_name': property.square.name,
        'houses': property.houses,
        'cost': construction_cost,
        'player_money': player.money
      }
    }

  @staticmethod
  def can_evenly_construct(color_group, game, property, number_of_houses):
    """
    Check the even-build rule for adding `number_of_houses` to `property`.

    Returns `(allowed, reason)`.
    """
    if color_group is None:
      return False, 'Property has no color group configured'

    others = list(
      Property.objects.filter(
        square__color_group=color_group,
        game=game,
      ).exclude(id=property.id).values_list('houses', flat=True)
    )

    if not others:
      # A single-property group has nothing to stay even with.
      return True, ''

    lowest = min(others)
    highest_before_last_house = property.houses + number_of_houses - 1

    if highest_before_last_house > lowest:
      headroom = max(0, lowest - property.houses + 1)
      return False, (
        f"Houses must be built evenly across {color_group.name}: "
        f"{property.square.name} has {property.houses} and the lowest in the group "
        f"is {lowest}, so you can add at most {headroom} here"
      )

    return True, ''

  @staticmethod
  @service_result
  def leave_game(game_id, player_id):
    try:
      game = Game.objects.select_related('created_by').prefetch_related('players').get(id=game_id)
    except Game.DoesNotExist:
      raise GameNotFound('Game not found')
    player = _get_player(player_id)

    if not game.players.filter(id=player.id).exists():
      raise InvalidAction('You are not in this game')

    if game.state == Game.GameState.FINISHED:
      raise InvalidGameState('Game is already finished')

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
      if new_creator:
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
