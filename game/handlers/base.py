import functools
import logging

from channels.db import database_sync_to_async

from game.db_utils import DbUtils
from game.exceptions import GameError, PlayerNotFound

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


async def run_action(consumer, data, service_fn, *extra_args):
  """
  Resolve the calling player, run `service_fn(game_id, player_id, *extra_args)`
  off the event loop, and send a clean error if it failed.

  Every handler was repeating "resolve the player (raising `PlayerNotFound`
  if there isn't one), call the service, bail out with `send_error` if it
  wasn't successful" by hand - inconsistently: a few handlers skipped the
  player check entirely, risking a bare `AttributeError` (caught by
  `ws_handler`'s generic branch as an unhelpful "something went wrong")
  instead of a clean "Player not found". This is that one path.

  Returns the service result dict on success, or `None` after already
  sending the error - the caller should just `return` in that case.
  """
  player = await DbUtils.get_player(data.get('user'))
  if not player:
    raise PlayerNotFound('Player not found')

  result = await database_sync_to_async(service_fn)(
    data.get('game_id'), player.id, *extra_args
  )

  if not result['success']:
    await consumer.send_error(result['message'])
    return None

  return result


async def broadcast(consumer, event_type, data):
  """Send `data` to every connection in this game's room."""
  await consumer.channel_layer.group_send(
    consumer.room_group_name,
    {'type': event_type, 'data': data}
  )
