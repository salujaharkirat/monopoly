"""
Turn order for a Game's players.

`Game.players` is a plain ManyToManyField with no `through` model, so Django
gives no ordering guarantee over `.all()`
"""

from game.models import Game, Player


def _ordered_membership_rows(game):
  """
  Rows of the M2M join table for `game`, in join order.

  Ordered by the join table's own auto-increment id - not `Player.id` (that
  reflects account creation, not when this player joined this game) and not
  `Player.created_at` for the same reason.
  """
  return Game.players.through.objects.filter(game=game).order_by('id')


def get_ordered_players(game):
  """
  Players in `game`, in the order they joined.

  Deterministic, unlike `game.players.all()`.
  """
  rows = list(_ordered_membership_rows(game))
  players_by_id = {
    p.id: p for p in Player.objects.filter(id__in=[row.player_id for row in rows])
  }
  return [players_by_id[row.player_id] for row in rows if row.player_id in players_by_id]


def get_current_player(game):
  """
  The player whose turn it is, resolved by position in join order.
  """
  players = get_ordered_players(game)
  if not players:
    return None
  return players[game.current_player_index % len(players)]


def advance_turn(game):
  """
  Move to the next player in join order and bump the turn counter.
  """
  players = get_ordered_players(game)
  if not players:
    raise ValueError('Cannot advance turn: game has no players')

  game.current_player_index = (game.current_player_index + 1) % len(players)
  game.turn_number += 1
  game.save()
  return players[game.current_player_index]
