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
  Players in `game`, in the order they joined - active and bankrupt alike.

  Deterministic, unlike `game.players.all()`
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


def _next_active_index(players, start_index, exclude_id=None):
  """
  Walk forward from `start_index` (exclusive), returning the index of the
  first active player - also skipping `exclude_id` if given. `None` if no
  such player exists.
  """
  for step in range(1, len(players) + 1):
    index = (start_index + step) % len(players)
    candidate = players[index]
    if candidate.is_active and candidate.id != exclude_id:
      return index
  return None


def advance_turn(game):
  """
  Move to the next active player in join order and bump the turn counter.

  Steps forward one seat at a time, skipping bankrupt players, so a seat
  going inactive mid-rotation never skips or double-counts anyone else.
  """
  players = get_ordered_players(game)
  if not players:
    raise ValueError('Cannot advance turn: game has no players')

  index = _next_active_index(players, game.current_player_index)
  if index is None:
    raise ValueError('Cannot advance turn: no active players')

  game.current_player_index = index
  game.turn_number += 1
  game.save()
  return players[index]


def remove_player(game, player):
  """
  Remove `player` from the game's turn rotation for good (leaving the game,
  as opposed to going bankrupt - which keeps the seat but flips `is_active`).

  Removing a seat from the join table shortens `get_ordered_players`, which
  would otherwise reindex everyone after it. To keep whose-turn-it-is
  stable across that: if `player` wasn't the current player, the same
  current player is re-pointed at their new index in the shorter list; if
  `player` WAS the current player, the next active player (excluding the
  one leaving) takes over instead.

  Returns the player now current, or `None` if nobody is left.
  """
  players = get_ordered_players(game)
  if not players:
    game.players.remove(player)
    return None

  current_index = game.current_player_index % len(players)
  current = players[current_index]

  if current.id == player.id:
    next_index = _next_active_index(players, current_index, exclude_id=player.id)
    target = players[next_index] if next_index is not None else None
  else:
    target = current

  game.players.remove(player)

  if target is None:
    game.current_player_index = 0
    game.save()
    return None

  new_players = get_ordered_players(game)
  game.current_player_index = next(
    i for i, p in enumerate(new_players) if p.id == target.id
  )
  game.save()
  return target
