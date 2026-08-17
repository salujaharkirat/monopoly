from abc import ABC
from game.rent_calculator import RentCalculator
from models import Player, Square, Game, Property
import random

from constants import CHANCE_CARDS, COMMUNITY_CHEST_CARDS
from strategies.card_strategy import CardStrategyFactory
from enums import SquareType

class SquareStrategy(ABC):
  def execute(self, player: Player, square: Square, game: Game):
    pass

class GoSquareStrategy(SquareStrategy):
  def execute(self, player: Player, square: Square, game: Game):
    return {
      'message': f"{player.user.username} collected $200"
    }

class PropertySquareStrategy(SquareStrategy):
  def execute(self, player: Player, square: Square, game: Game):
    property = Property.objects.get(square=square)
    if property.owner:
      if property.owner.id != player.id:
        rent = RentCalculator.calculate_rent(game, property)
        if player.money < rent:
          return {
            'message': f"Cannot pay ${rent} for player {player.user.username}"
          }
        player.money -= rent
        property.owner.money += rent
        player.save()
        property.owner.save()
        return {
          'message': f"Paid ${rent} to {property.owner.user.username}"
        }
      return {
        'message': f"Owned by {player.user.username}"
      }
    return {
      'message': f"Property available for ${square.price}",
      'can_buy': True,
      'price': square.price
    }

class TaxSquareStrategy(SquareStrategy):
  def execute(self, player: Player, square: Square, game: Game):
    tax_amount = square.tax_amount or 100
    player.money -= tax_amount
    player.save()
    return {
      'message': f"Paid ${tax_amount} in taxes"
    }

class GoToJailSquareStrategy(SquareStrategy):
  def execute(self, player: Player, square: Square, game: Game):
    player.position = 10
    player.is_in_jail = True
    player.save()
    return {
      'message': 'Go to Jail!'
    }

class ChanceSquareStrategy(SquareStrategy):
  def handle_chance_card(self, player, game):
    card = random.choice(CHANCE_CARDS)
    card_type = card.get('type')
    strategy = CardStrategyFactory.get_strategy(card_type)
    result = strategy.execute(player, game, card)
    result['success'] = True
    result['card'] = card

    return result

  def execute(self, player: Player, square: Square, game: Game):
    result = {
      'message': "Chance card drawn"
    }
    chance_card_result = self.handle_chance_card(player, game)
    if chance_card_result['success']:
      result['card'] = chance_card_result
      result['message'] = f"{chance_card_result['card_name']}: {chance_card_result['description']}"
      if chance_card_result.get("amount"):
        result['message'] += f" (${chance_card_result['amount']})"
      else:
        result['message'] = f"Chance: {chance_card_result['message']}"

    return result

class CommunityChestSquareStrategy(SquareStrategy):
  def handle_community_card(self, player, game):
    card = random.choice(COMMUNITY_CHEST_CARDS)
    card_type = card.get('type')
    strategy = CardStrategyFactory.get_strategy(card_type)
    result = strategy.execute(player, game, card)
    result['success'] = True
    result['card'] = card
    return result
  
  def execute(self, player: Player, square: Square, game: Game):
    result = {
      'message': 'Community chest drawn'
    }

    community_card_result = self.handle_community_card(player, game)
    if community_card_result['success']:
      result['card'] = community_card_result
      result['message'] = f"{community_card_result['card_name']}: {community_card_result['description']}"
      if community_card_result.get("amount"):
        result['message'] += f" (${community_card_result['amount']})"
      else:
        result['message'] = f"Chance: {community_card_result['message']}"

    return result

class SquareStrategyFactory:
  _strategies = {
    SquareType.GO: GoSquareStrategy(),
    SquareType.PROPERTY: PropertySquareStrategy(),
    SquareType.TAX: TaxSquareStrategy(),
    SquareType.GO_TO_JAIL: GoToJailSquareStrategy(),
    SquareType.CHANCE: ChanceSquareStrategy(),
    SquareType.COMMUNITY_CHEST: CommunityChestSquareStrategy(),
    SquareType.RAIL_ROAD: PropertySquareStrategy(),
  }

  @classmethod
  def get_strategy(cls, type):
    strategy = cls._strategies.get(type)
    if not strategy:
      raise ValueError(f"strategy not found ${strategy}")

    return strategy
  