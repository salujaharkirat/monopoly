from abc import ABC, abstractmethod

from game import bank, bankruptcy, jail
from game.game_player import resolve as resolve_game_player
from game.models import GamePlayer, Square, Game, Property
from game.enums import CardType
from game.rent_calculator import RentCalculator


class CardStrategy(ABC):
  """
  Applies one drawn card to the game.

  Every strategy returns at least ``{'amount': int, 'message': str}``. The
  card's own `name`/`description` are merged in by the caller
  (`CardSquareStrategy`), so no strategy has to remember to echo them back.

  `bank_module`/`bankruptcy_module` are injected (defaulting to the real
  `bank`/`bankruptcy` modules) so a subclass that moves money can be
  unit-tested against a fake ledger - asserting on the message/branching a
  bankruptcy outcome produces - without needing to actually drain a
  `GamePlayer`'s money to exactly zero to exercise that branch.
  """

  def __init__(self, bank_module=bank, bankruptcy_module=bankruptcy):
    self._bank = bank_module
    self._bankruptcy = bankruptcy_module

  @abstractmethod
  def execute(self, game_player: GamePlayer, square: Square, game: Game, card: dict):
    ...


class CollectMoneyStrategy(CardStrategy):
  def execute(self, game_player: GamePlayer, square: Square, game: Game, card: dict):
    amount = card.get('amount', 0)
    self._bank.transfer(None, game_player, amount)
    return {
      'amount': amount,
      'message': f"Collected ${amount}"
    }


class PayMoneyStrategy(CardStrategy):
  def execute(self, game_player: GamePlayer, square: Square, game: Game, card: dict):
    amount = card.get('amount', 0)
    result = self._bankruptcy.settle_debt(game_player, None, amount)

    if result['is_bankrupt']:
      return {
        'amount': result['paid_amount'],
        'message': f"Went bankrupt paying ${amount} (paid ${result['paid_amount']})",
        'is_bankrupt': result['is_bankrupt']
      }

    return {
      'amount': result['paid_amount'],
      'message': f"Paid ${result['paid_amount']}"
    }


class AdvanceToGoStrategy(CardStrategy):
  def execute(self, game_player: GamePlayer, square: Square, game: Game, card: dict):
    game_player.position = 0
    game_player.save(update_fields=['position'])
    self._bank.transfer(None, game_player, 200)
    return {
      'amount': 200,
      'message': "Advanced to GO and collected $200"
    }


class AdvanceToPropertyStrategy(CardStrategy):
  def execute(self, game_player: GamePlayer, square: Square, game: Game, card: dict):
    target_position = card.get('position', 0)
    property_name = card.get('property_name')
    old_position = game_player.position

    result = {
      'amount': 0,
      'message': f"Moved to {property_name}",
      'new_position': target_position,
      'property_name': property_name,
      'can_buy': False,
      'price': 0,
      'is_bankrupt': False
    }

    # Moving forward past GO pays $200; moving to a lower position means the
    # board wrapped around.
    if target_position < old_position:
      self._bank.transfer(None, game_player, 200)
      result['amount'] = 200
      result['message'] = f"Moved to {property_name} and collected $200 for passing GO"

    game_player.position = target_position
    game_player.save(update_fields=['position'])

    property = Property.objects.select_related('square', 'owner').get(
      square__position=target_position, game=game
    )

    if property.owner and property.owner.id != game_player.player.id:
      rent = RentCalculator.calculate_rent(game, property)
      owner_game_player = resolve_game_player(game, property.owner)
      bankruptcy_result = self._bankruptcy.settle_debt(game_player, owner_game_player, rent)

      if bankruptcy_result['is_bankrupt']:
        result['message'] += f"Went bankrupt paying ${rent} (paid ${bankruptcy_result['paid_amount']})"
        result['is_bankrupt'] = True
        return result

      result['amount'] = bankruptcy_result['paid_amount']
      result['message'] += f" - Paid ${bankruptcy_result['paid_amount']} rent to {property.owner.user.username}"
    elif not property.owner:
      result['can_buy'] = True
      if property.square:
        result['price'] = property.square.price
      result['property_id'] = property.id

    return result


class MoveBackStrategy(CardStrategy):
  def execute(self, game_player: GamePlayer, square: Square, game: Game, card: dict):
    spaces = card.get('spaces', 0)
    game_player.position = (game_player.position - spaces) % 40
    # TODO: Add rent, tax, go to jail
    game_player.save()
    return {
      'amount': 0,
      'message': f"Moved back {spaces} spaces",
      'new_position': game_player.position,
    }


class GoToJailStrategy(CardStrategy):
  def execute(self, game_player: GamePlayer, square: Square, game: Game, card: dict):
    jail.send_to_jail(game_player)
    return {
      'amount': 0,
      'message': "Go to Jail!",
      'new_position': jail.JAIL_POSITION,
    }


class GetOutOfJailStrategy(CardStrategy):
  def execute(self, game_player: GamePlayer, square: Square, game: Game, card: dict):
    game_player.get_out_of_jail_cards += 1
    game_player.save(update_fields=['get_out_of_jail_cards'])
    return {
      'amount': 0,
      'message': "Get Out of Jail Free - keep this card until you need it",
    }


class RepairsStrategy(CardStrategy):
  """Charge per house and per hotel across everything the player owns."""

  def execute(self, game_player: GamePlayer, square: Square, game: Game, card: dict):
    house_cost = card.get('house_cost', 0)
    hotel_cost = card.get('hotel_cost', 0)

    owned = Property.objects.filter(owner=game_player.player, game=game)
    houses = sum(p.houses for p in owned if p.houses < 5)
    hotels = sum(1 for p in owned if p.houses >= 5)

    total_cost = (houses * house_cost) + (hotels * hotel_cost)

    if total_cost == 0:
      return {'amount': 0, 'message': "No buildings to repair"}

    # Bankruptcy impact
    result = self._bankruptcy.settle_debt(game_player, None, total_cost)

    if result['is_bankrupt']:
      return {
        'amount': result['paid_amount'],
        'is_bankrupt': True,
        'message': f"Went bankrupt paying ${total_cost} (paid ${result['paid_amount']})"
      }

    return {
      'amount': result['paid_amount'],
      'message': f"Repairs on {houses} house(s) and {hotels} hotel(s) cost ${total_cost}",
    }


class PayEachPlayerStrategy(CardStrategy):
  def execute(self, game_player: GamePlayer, square: Square, game: Game, card: dict):
    # Bankruptcy impact
    amount = card.get('amount', 0)
    total_paid = 0
    other_players = list(
      game.game_players.exclude(id=game_player.id).select_related('player__user')
    )
    total_amount = amount * len(other_players)

    is_bankrupt = not self._bankruptcy.has_sufficient_amount(game_player, total_amount)
    per_player_amount = (game_player.money // len(other_players)) if is_bankrupt else amount

    for p in other_players:
      self._bank.transfer(game_player, p, per_player_amount)
      total_paid += per_player_amount

    if is_bankrupt:
      self._bankruptcy.go_bankrupt(game_player)
      return {
        'amount': total_paid,
        'is_bankrupt': True,
        'message': f"Went bankrupt paying ${total_amount} to other players (paid ${total_paid})",
        'paid_to': [p.player.user.username for p in other_players]
      }

    return {
      'amount': total_paid,
      'message': f"Paid ${total_paid} total to other players",
      'paid_to': [p.player.user.username for p in other_players]
    }


class CollectFromAllStrategy(CardStrategy):
  def execute(self, game_player: GamePlayer, square: Square, game: Game, card: dict):
    amount = card.get('amount', 0)
    total_collected = 0
    for p in game.game_players.exclude(id=game_player.id):
      payable = min(amount, p.money)
      self._bank.transfer(p, None, payable)
      total_collected += payable

    self._bank.transfer(None, game_player, total_collected)
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
