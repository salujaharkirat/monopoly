from abc import ABC, abstractmethod

from game.models import Player, Square, Game, Property
from game.enums import CardType
from game.rent_calculator import RentCalculator


class CardStrategy(ABC):
  """
  Applies one drawn card to the game.

  Every strategy returns at least ``{'amount': int, 'message': str}``. The
  card's own `name`/`description` are merged in by the caller
  (`CardSquareStrategy`), so no strategy has to remember to echo them back.
  """

  @abstractmethod
  def execute(self, player: Player, square: Square, game: Game, card: dict):
    ...


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
    target_position = card.get('position', 0)
    property_name = card.get('property_name')
    old_position = player.position

    result = {
      'amount': 0,
      'message': f"Moved to {property_name}",
      'new_position': target_position,
      'property_name': property_name,
      'can_buy': False,
      'price': 0,
    }

    # Moving forward past GO pays $200; moving to a lower position means the
    # board wrapped around.
    if target_position < old_position:
      player.money += 200
      result['amount'] = 200
      result['message'] = f"Moved to {property_name} and collected $200 for passing GO"

    player.position = target_position
    player.save()

    property = Property.objects.select_related('square', 'owner').get(
      square__position=target_position, game=game
    )

    if property.owner and property.owner.id != player.id:
      rent = RentCalculator.calculate_rent(game, property)
      if player.money < rent:
        result['message'] += f" - not enough money to pay ${rent} rent"
        return result

      player.money -= rent
      property.owner.money += rent
      property.owner.save()
      player.save()
      result['amount'] = rent
      result['message'] += f" - Paid ${rent} rent to {property.owner.user.username}"
    elif not property.owner:
      result['can_buy'] = True
      if property.square:
        result['price'] = property.square.price
      result['property_id'] = property.id

    return result


class MoveBackStrategy(CardStrategy):
  def execute(self, player: Player, square: Square, game: Game, card: dict):
    spaces = card.get('spaces', 0)
    player.position = (player.position - spaces) % 40
    player.save()
    return {
      'amount': 0,
      'message': f"Moved back {spaces} spaces",
      'new_position': player.position,
    }


class GoToJailStrategy(CardStrategy):
  def execute(self, player: Player, square: Square, game: Game, card: dict):
    player.position = 10
    player.is_in_jail = True
    player.save()
    return {
      'amount': 0,
      'message': "Go to Jail!",
      'new_position': 10,
    }


class GetOutOfJailStrategy(CardStrategy):
  def execute(self, player: Player, square: Square, game: Game, card: dict):
    # Retaining the card needs per-player card storage
    # (Player.get_out_of_jail_cards), which arrives with the jail rework.
    # Registered now so drawing it stops crashing the roll.
    return {
      'amount': 0,
      'message': "Get Out of Jail Free - holding this card is not supported yet",
    }


class RepairsStrategy(CardStrategy):
  """Charge per house and per hotel across everything the player owns."""

  def execute(self, player: Player, square: Square, game: Game, card: dict):
    house_cost = card.get('house_cost', 0)
    hotel_cost = card.get('hotel_cost', 0)

    owned = Property.objects.filter(owner=player, game=game)
    houses = sum(p.houses for p in owned if p.houses < 5)
    hotels = sum(1 for p in owned if p.houses >= 5)

    total_cost = (houses * house_cost) + (hotels * hotel_cost)

    if total_cost == 0:
      return {'amount': 0, 'message': "No buildings to repair"}

    paid = min(total_cost, player.money)
    player.money -= paid
    player.save()

    return {
      'amount': paid,
      'message': f"Repairs on {houses} house(s) and {hotels} hotel(s) cost ${total_cost}",
    }


class PayEachPlayerStrategy(CardStrategy):
  def execute(self, player: Player, square: Square, game: Game, card: dict):
    amount = card.get('amount', 0)
    total_paid = 0
    for p in game.players.all():
      if player.id == p.id:
        continue
      payable = min(amount, player.money)
      if payable <= 0:
        break
      player.money -= payable
      p.money += payable
      total_paid += payable
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
      if p.id == player.id:
        continue
      payable = min(amount, p.money)
      p.money -= payable
      total_collected += payable
      p.save()

    player.money += total_collected
    player.save()
    return {
      'amount': total_collected,
      'message': f"Collected ${total_collected} from other players"
    }


class CardStrategyFactory:
  _strategies = {
    CardType.COLLECT_MONEY: CollectMoneyStrategy(),
    CardType.PAY_MONEY: PayMoneyStrategy(),
    CardType.ADVANCE_TO_GO: AdvanceToGoStrategy(),
    CardType.GO_TO_JAIL: GoToJailStrategy(),
    CardType.GET_OUT_OF_JAIL: GetOutOfJailStrategy(),
    CardType.ADVANCE_TO_PROPERTY: AdvanceToPropertyStrategy(),
    CardType.COLLECT_FROM_ALL: CollectFromAllStrategy(),
    CardType.PAY_EACH_PLAYER: PayEachPlayerStrategy(),
    CardType.GENERAL_REPAIRS: RepairsStrategy(),
    CardType.STREET_REPAIRS: RepairsStrategy(),
    CardType.MOVE_BACK: MoveBackStrategy(),
  }

  @classmethod
  def get_strategy(cls, card_type):
    strategy = cls._strategies.get(card_type)
    if strategy is None:
      # A missing strategy is a programming error, not a rule violation, so it
      # must not be a GameError.
      raise ValueError(f"No card strategy registered for {card_type!r}")

    return strategy
