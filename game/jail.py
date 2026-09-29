from game.models import Player

JAIL_POSITION = 10


def send_to_jail(player: Player):
  """
  Send `player` to jail - landing on Go To Jail, drawing the matching card,
  or rolling doubles three times in a row.

  Resets `doubles_count` and `has_rolled` since the turn that (maybe) caused
  this ends regardless, and a clean slate is needed for whenever this player
  is next able to roll (after paying bail / using a card).
  """
  player.position = JAIL_POSITION
  player.is_in_jail = True
  player.doubles_count = 0
  player.has_rolled = False
  player.save()
