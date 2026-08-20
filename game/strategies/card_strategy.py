from abc import ABC
from game.models import Player, Square, Game, Property
from game.enums import CardType


class CardStrategy(ABC):
  def execute(self, player: Player, square: Square, game: Game, card: dict):
    pass

class CollectMoneyStrategy(CardStrategy):
  def execute(self, player: Player, square: Square, game: Game, card: dict):
    amount = card.get('amount', 0)
    player.money += amount
    player.save()
    return {
      'amount': amount,
      'message': f"Collected ${amount}"
    }

class PayMoneyStrategy(CardStrategy):
  def execute(self, player: Player, square: Square, game: Game, card: dict):
    amount = card.get('amount', 0)
    if player.money < amount:
      return {
        'amount': 0,
        'message': f"Not enough money to pay ${amount}"
      }
    player.money -= amount
    player.save()
    return {
      'amount': amount,
      'message': f"Paid ${amount}"
    }

class AdvanceToGoStrategy(CardStrategy):
  def execute(self, player: Player, square: Square, game: Game, card: dict):
    player.position = 0
    player.money += 200
    player.save()
    return {
      'amount': 200,
      'message': "Advanced to GO and collected $200"
    }

class AdvanceToPropertyStrategy(CardStrategy):
  def execute(self, player: Player, square: Square, game: Game, card: dict):
    result = {
      'amount': 0,
      'message': '',
      'new_position': 0,
      'property_name': '',
      'can_buy': False,
      'price': 0
    }
    target_position = card.get('position', 0)
    property_name = card.get('property_name')
    

    old_position = player.position

    if target_position < old_position:
      player.money += 200
      result['amount'] = 200
      result['message'] = f"Moved to {property_name} and collected $200 for passing GO"
    else:
      result['message'] = f"Moved to {property_name}"

    result['new_position'] = target_position
    result['property_name'] = property_name

    property = Property.objects.get(square__position=target_position, game=game)
    if property.owner:
      if property.owner.id != player.id:
        # TODO: Add houses/hotels logic later
        rent = property.square.rent or 0
        if player.money < rent:
          return {
            'amount': 0,
            'message': f"Not enough money to pay ${rent} rent on {property_name}"
          }

        player.money -= rent
        property.owner.money += rent
        property.owner.save()
        player.save()
        result['amount'] = rent
        result['message'] += f" - Paid ${rent} rent to {property.owner.user.username}"
    else:
      result['can_buy'] = True
      result['price'] = property.square.price
      result['property_id'] = property.id

    return result


class MoveBackStrategy(CardStrategy):
  def execute(self, player: Player, square: Square, game: Game, card: dict):
    spaces = card.get('spaces', 0)
    new_position = (player.position - spaces) % 40
    player.position = new_position
    player.save()
    return {
      'amount': 0,
      'message': f"Moved back ${spaces}"
    }
    


class GoToJailStrategy(CardStrategy):
  def execute(self, player: Player, square: Square, game: Game, card: dict):
    player.position = 10
    player.is_in_jail = True
    player.save()
    return {
      'amount': 0,
      'message': "Go to Jail!"
    }

class GeneralRepairsStrategy(CardStrategy):
  # TODO: Add houses/hotels logic later
  def execute(self, player: Player, square: Square, game: Game, card: dict):
    total_cost = 0
    return {
      'amount': total_cost,
      'message': f"General repair cost ${total_cost}"
    }

class PayEachPlayerStrategy(CardStrategy):
  def execute(self, player: Player, square: Square, game: Game, card: dict):
    amount = card.get('amount', 0)
    total_paid = 0
    for p in game.players.all():
      if player.id != p.id:
        if player.money >= amount:
          player.money -= amount
          p.money += amount
          total_paid += amount
          p.save()
          player.save()
        else:
          p.money += player.money
          total_paid += player.money
          player.money = 0
          p.save()
          player.save()
    return {
      'amount': total_paid,
      'message': f"Paid ${total_paid} total to other players",
      'paid_to': [p.user.username for p in game.players.all() if p.id != player.id]
    }

class CollectFromAllStrategy(CardStrategy):
  def execute(self, player: Player, square: Square, game: Game, card: dict):
    amount = card.get('amount', 0)
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
    return {
      'amount': total_collected,
      'message': f"Collected ${total_collected} from other players"
    }

class StreetRepairsStrategy(CardStrategy):
  def execute(self, player: Player, square: Square, game: Game, card: dict):
    # TODO: Add houses/hotels logic later
    total_cost = 0
    return {
      'amount': total_cost,
      'message': f"Street repair cost ${total_cost}"
    }


class CardStrategyFactory:
  _strategies = {
    CardType.COLLECT_MONEY: CollectMoneyStrategy(),
    CardType.PAY_MONEY: PayMoneyStrategy(),
    CardType.ADVANCE_TO_GO: AdvanceToGoStrategy(),
    CardType.GO_TO_JAIL: GoToJailStrategy(),
    CardType.ADVANCE_TO_PROPERTY: AdvanceToPropertyStrategy(),
    CardType.COLLECT_FROM_ALL: CollectFromAllStrategy(),
    CardType.PAY_EACH_PLAYER: PayMoneyStrategy(),
    CardType.GENERAL_REPAIRS: GeneralRepairsStrategy(),
    CardType.STREET_REPAIRS: StreetRepairsStrategy(), 
    CardType.MOVE_BACK: MoveBackStrategy(),
  }

  @classmethod
  def get_strategy(cls, type):
    strategy = cls._strategies.get(type)
    if not strategy:
      raise ValueError(f"strategy not found ${strategy}")

    return strategy