import functools
import logging

from game.exceptions import GameError

logger = logging.getLogger(__name__)

INTERNAL_ERROR_MESSAGE = 'Something went wrong handling that action.'


def ws_handler(func):
  """
  Error boundary for WebSocket action handlers.

  A `GameError` is a rule violation and is sent to the player as-is. Anything
  else is a bug: it is logged with a full traceback and the player gets a
  generic message, so internal details never leak into the UI and the failure
  is still visible in the logs.

  The socket stays open either way - one bad action should not drop the player
  out of the game.
  """
  @functools.wraps(func)
  async def wrapper(consumer, data):
    try:
      return await func(consumer, data)
    except GameError as exc:
      await consumer.send_error(str(exc))
    except Exception:
      logger.exception(f"Unhandled error in {func.__name__} (game_id={data.get('game_id')}, user={getattr(data.get('user'), 'username', None)})")
      await consumer.send_error(INTERNAL_ERROR_MESSAGE)
  return wrapper
