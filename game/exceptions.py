"""Domain exceptions for the game app.

`GameError` and its subclasses are *rule violations* - things a player tried to
do that the game legitimately refuses ("not your turn", "you can't afford
that"). They carry a message intended for the player and are converted into
``{'success': False, 'message': ...}`` at the service boundary by
:func:`game.service.service_result`.

Anything that is not a `GameError` is a bug. It is logged with a traceback and
allowed to propagate, instead of being reported to the player as though it were
a rule. That distinction is the whole point of this module: an `AttributeError`
must never look like "not your turn".
"""


class GameError(Exception):
  """
  Base class for player-visible rule violations.

  Extra keyword arguments are carried through to the service response, so a
  refusal can ship structured data alongside its message::

  raise PlayerBankrupt("Player is bankrupt", bankrupt=True)
  # -> {'success': False, 'message': 'Player is bankrupt',
  #     'error': 'PlayerBankrupt', 'bankrupt': True}
  """

  def __init__(self, message, **payload):
    super().__init__(message)
    self.payload = payload


# --- Lookup failures -------------------------------------------------------

class GameNotFound(GameError):
  pass


class PlayerNotFound(GameError):
  pass


class PropertyNotFound(GameError):
  pass


class SquareNotFound(GameError):
  pass


# --- Turn / state violations ----------------------------------------------

class InvalidGameState(GameError):
  """The game is not in a state where this action makes sense."""


class NotYourTurn(GameError):
  pass


class NotAuthorized(GameError):
  """The player is not allowed to perform this action (e.g. not the creator)."""


class PlayerInJail(GameError):
  pass


class NotInJail(GameError):
  """Trying to pay bail or use a jail card while not in jail."""


class NoJailCardsAvailable(GameError):
  """Trying to use a Get Out of Jail Free card while holding none."""


class PlayerBankrupt(GameError):
  pass


# --- Action-specific violations -------------------------------------------

class InvalidAction(GameError):
  """The action is well-formed but not legal right now."""


class InsufficientFunds(GameError):
  pass


class PropertyNotPurchasable(GameError):
  pass


class PropertyAlreadyOwned(GameError):
  pass


class NotPropertyOwner(GameError):
  pass


class BuildRuleViolation(GameError):
  """Building would break the monopoly / even-build / max-houses rules."""
