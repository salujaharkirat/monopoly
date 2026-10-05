"""
Turn order for a Game's players.

`GamePlayer` is the explicit `through` model for `Game.players`, so each row
*is* one seat in join order - no separate join table to reach into, and no
re-fetching `Player` rows by id the way a plain, implicit M2M would require.
"""

from game.models import GamePlayer


def get_ordered_players(game):
  """
  `GamePlayer` rows for `game`, in the order those players joined - active
  and bankrupt alike.

  Ordered by the row's own auto-increment id - not `Player.id` (that
  reflects account creation, not when this player joined this game) and not
  `Player.created_at` for the same reason.
  """
  return list(GamePlayer.objects.filter(game=game).order_by('id'))


def get_current_player(game):
  """
  The `GamePlayer` whose turn it is, resolved by position in join order.
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


def remove_player(game, game_player):
  """
  Remove `game_player`'s seat from the game's turn rotation for good
  (leaving the game, as opposed to going bankrupt - which keeps the seat but
  flips `is_active`).

  Removing a seat shortens `get_ordered_players`, which would otherwise
  reindex everyone after it. To keep whose-turn-it-is stable across that:
  if `game_player` wasn't current, the same current player is re-pointed at
  their new index in the shorter list; if `game_player` WAS current, the
  next active player (excluding the one leaving) takes over instead.

  Returns the `GamePlayer` now current, or `None` if nobody is left.
  """
  players = get_ordered_players(game)
  if not players:
    game_player.delete()
    return None

  current_index = game.current_player_index % len(players)
  current = players[current_index]

  if current.id == game_player.id:
    next_index = _next_active_index(players, current_index, exclude_id=game_player.id)
    target = players[next_index] if next_index is not None else None
  else:
    target = current

  game_player.delete()

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
