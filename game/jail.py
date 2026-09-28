from game.models import Player

JAIL_POSITION = 10


def send_to_jail(player: Player):
  """
  Send `player` to jail - landing on Go To Jail, drawing the matching card,
  or rolling doubles three times in a row.

  Resets `doubles_count` since the streak that (maybe) caused this ends the
  turn regardless.
  """
  player.position = JAIL_POSITION
  player.is_in_jail = True
  player.doubles_count = 0
  player.save()
