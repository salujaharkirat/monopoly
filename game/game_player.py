from game.models import GamePlayer
from game.exceptions import InvalidAction


def resolve(game, player):
  """The per-game row for `player` in `game` - raises if they're not in it."""
  try:
    return GamePlayer.objects.select_related('player__user').get(game=game, player=player)
  except GamePlayer.DoesNotExist:
    raise InvalidAction('You are not in this game')
