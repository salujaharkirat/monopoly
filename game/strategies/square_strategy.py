import random
from abc import ABC, abstractmethod

from game.rent_calculator import RentCalculator
from game.models import Player, Square, Game, Property

from game.constants import CHANCE_CARDS, COMMUNITY_CHEST_CARDS
from game.strategies.card_strategy import CardStrategyFactory
from game.enums import SquareType


class SquareStrategy(ABC):
  """
  Applies the effect of landing on one kind of square.

  `dice_roll` is the total the player just rolled. Utility rent is a multiple
  of it, so it has to travel all the way down from `roll_dice`.
  """

  @abstractmethod
  def execute(self, player: Player, square: Square, game: Game, dice_roll: int = 0):
    ...


class NoOpSquareStrategy(SquareStrategy):
  """For squares that do nothing on landing (Free Parking, Just Visiting)."""

  def __init__(self, message):
    self._message = message

  def execute(self, player: Player, square: Square, game: Game, dice_roll: int = 0):
    return {'message': self._message}


class GoSquareStrategy(SquareStrategy):
  def execute(self, player: Player, square: Square, game: Game, dice_roll: int = 0):
    return {
      'message': f"{player.user.username} landed on GO"
    }


class PropertySquareStrategy(SquareStrategy):
  """Handles properties, railroads and utilities - anything ownable."""

  def execute(self, player: Player, square: Square, game: Game, dice_roll: int = 0):
    property = Property.objects.select_related('square', 'owner').get(
      square=square, game=game
    )

    if not property.owner:
      return {
        'message': f"{square.name} available for ${square.price}",
        'can_buy': True,
        'price': square.price,
        'property_id': property.id,
      }

    if property.owner.id == player.id:
      return {
        'message': f"You already own {square.name}"
      }

    if property.is_mortgaged:
      return {
        'message': f"{square.name} is mortgaged - no rent due"
      }

    rent = RentCalculator.calculate_rent(game, property, dice_roll)

    if player.money < rent:
      # Partial payment and bankruptcy are handled by the bankruptcy rework;
      # for now the debt is reported but not collected.
      return {
        'message': f"{player.user.username} cannot pay ${rent} rent to {property.owner.user.username}",
        'rent_due': rent,
      }

    player.money -= rent
    property.owner.money += rent
    player.save()
    property.owner.save()

    return {
      'message': f"Paid ${rent} rent to {property.owner.user.username}",
      'rent_paid': rent,
    }


class TaxSquareStrategy(SquareStrategy):
  def execute(self, player: Player, square: Square, game: Game, dice_roll: int = 0):
    tax_amount = square.tax_amount or 100
    player.money -= tax_amount
    player.save()
    return {
      'message': f"Paid ${tax_amount} in taxes",
      'amount': tax_amount,
    }


class GoToJailSquareStrategy(SquareStrategy):
  def execute(self, player: Player, square: Square, game: Game, dice_roll: int = 0):
    player.position = 10
    player.is_in_jail = True
    player.save()
    return {
      'message': 'Go to Jail!',
      'new_position': 10,
    }


class CardSquareStrategy(SquareStrategy):
  """
  Draws from a deck and delegates to the matching card strategy.

  Chance and Community Chest differ only by deck and label, so they share this
  one implementation.
  """

  def __init__(self, deck, deck_name, label):
    self._deck = deck
    self._deck_name = deck_name
    self._label = label

  def draw(self):
    return random.choice(self._deck)

  def execute(self, player: Player, square: Square, game: Game, dice_roll: int = 0):
    card = self.draw()
    strategy = CardStrategyFactory.get_strategy(card.get('type'))
    outcome = strategy.execute(player, square, game, card)

    card_name = card.get('name', 'Card')
    description = card.get('description', '')

    message = f"{self._label}: {card_name} - {description}"
    amount = outcome.get('amount') or 0
    if amount:
      message += f" (${amount})"

    return {
      **outcome,
      'message': message,
      'card_name': card_name,
      'description': description,
      # The UI's card modal reads the card definition and the outcome from
      # this single object, so they are merged with the outcome winning.
      'card': {
        **card,
        **outcome,
        'deck': self._deck_name,
        'card_name': card_name,
        'description': description,
      },
    }


class SquareStrategyFactory:
  _strategies = {
    SquareType.GO: GoSquareStrategy(),
    SquareType.PROPERTY: PropertySquareStrategy(),
    SquareType.RAIL_ROAD: PropertySquareStrategy(),
    SquareType.UTILITY: PropertySquareStrategy(),
    SquareType.TAX: TaxSquareStrategy(),
    SquareType.GO_TO_JAIL: GoToJailSquareStrategy(),
    SquareType.JAIL: NoOpSquareStrategy('Just visiting jail'),
    SquareType.FREE_PARKING: NoOpSquareStrategy('Free parking - nothing happens'),
    SquareType.CHANCE: CardSquareStrategy(CHANCE_CARDS, 'chance', 'Chance'),
    SquareType.COMMUNITY_CHEST: CardSquareStrategy(
      COMMUNITY_CHEST_CARDS, 'community_chest', 'Community Chest'
    ),
  }

  @classmethod
  def get_strategy(cls, square_type):
    strategy = cls._strategies.get(square_type)
    if strategy is None:
      # A missing strategy is a programming error, not a rule violation, so it
      # must not be a GameError.
      raise ValueError(f"No square strategy registered for {square_type!r}")

    return strategy
