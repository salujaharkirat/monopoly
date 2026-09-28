from game import bank
from game.models import Player


def settle_debt(from_player: Player, to_player=None, amount = 0):
  if not from_player:
    return {
      'is_bankrupt': False,
      'paid_amount': 0
    }
  
  if not has_sufficient_amount(from_player, amount):
    amount = min(amount, from_player.money)
    bank.transfer(from_player, to_player, amount)
    if from_player.is_active: 
      from_player.is_active = False
      from_player.save()
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