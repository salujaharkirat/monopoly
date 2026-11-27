from game import bank
from game.models import GamePlayer, Property


def settle_debt(from_player: GamePlayer, to_player=None, amount = 0):
  if not has_sufficient_amount(from_player, amount):
    amount = min(amount, from_player.money)
    bank.transfer(from_player, to_player, amount)
    go_bankrupt(from_player, to_player)
    return {
      'is_bankrupt': True,
      'paid_amount': amount
    }

  bank.transfer(from_player, to_player, amount)
  return {
    'is_bankrupt': False,
    'paid_amount': amount
  }

def has_sufficient_amount(player, amount = 0):
  return player.money >= amount

def mark_bankrupt(player):
  """The single place a player's `is_active` flips to False."""
  if player.is_active:
    player.is_active = False
    player.save()

def forfeit_properties(player: GamePlayer, creditor=None):
  owned = Property.objects.filter(owner=player.player, game=player.game)

  if creditor is None:
    owned.update(owner=None, houses=0, is_mortgaged=False)
  else:
    owned.update(owner=creditor.player, houses=0)

def go_bankrupt(player: GamePlayer, creditor=None):
  mark_bankrupt(player)
  forfeit_properties(player, creditor)
