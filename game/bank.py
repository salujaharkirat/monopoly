"""
The single place money moves between players (and the bank).
"""

from django.db.models import F
from game.models import GamePlayer


def transfer(from_player, to_player, amount):
  """
  Move `amount` from `from_player` to `to_player` - each a `GamePlayer` (this
  account's seat in this one game), or `None` for the bank.

  `from_player=None` means the amount is created by the bank (e.g. passing
  GO, a Collect Money card). `to_player=None` means the amount is destroyed
  by the bank (e.g. tax, buying a house or property).
  """
  if amount == 0:
    return


  if from_player is not None and amount > from_player.money:
    amount = from_player.money

  if from_player is not None:
    GamePlayer.objects.filter(id=from_player.id).update(money=F('money') - amount)
    from_player.money -= amount

  if to_player is not None:
    GamePlayer.objects.filter(id=to_player.id).update(money=F('money') + amount)
    to_player.money += amount
