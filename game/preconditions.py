"""
Shared precondition checks for `GameService` actions.

Every action was re-deriving its own "is this legal right now" checks by
hand, in whatever order seemed natural at the time - which is exactly how
several real bugs crept in this session: `buy_property` checked `is_active`
in a different spot than every other action, `end_turn` was missing a check
entirely, and a turn-ending side effect went in the wrong branch. These are
the handful of checks that actually repeat; call the ones a given action
needs, in order, instead of re-typing them.
"""

from game import turn_order
from game.exceptions import (
  InvalidGameState,
  NotYourTurn,
  PlayerBankrupt,
  PlayerInJail,
  NotInJail,
  InvalidAction,
)


def require_playing(game):
  if game.state != game.GameState.PLAYING:
    raise InvalidGameState('Game is not in playing state')


def require_current_player(game, game_player):
  current = turn_order.get_current_player(game)
  if current is None or current.id != game_player.id:
    raise NotYourTurn('Not your turn')


def require_active(game_player):
  if not game_player.is_active:
    raise PlayerBankrupt('Player is bankrupt')


def require_in_jail(game_player):
  if not game_player.is_in_jail:
    raise NotInJail('Player is not in jail')


def require_not_in_jail(game_player):
  if game_player.is_in_jail:
    raise PlayerInJail('Player is in jail. Pay $50 or use get out of jail card')


def require_not_rolled(game_player):
  if game_player.has_rolled:
    raise InvalidAction('Already rolled this turn - end your turn before rolling again')
