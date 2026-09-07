from game.db_utils import DbUtils
from game.exceptions import GameNotFound, InvalidGameState, NotAuthorized, PlayerNotFound
from game.handlers.base import ws_handler


@ws_handler
async def handle_start_game(consumer, data: dict):
  game_id = data.get('game_id')
  player = await DbUtils.get_player(data.get('user'))
  game = await DbUtils.get_game(game_id)

  if not player:
    raise PlayerNotFound('Player not found')

  if not game:
    raise GameNotFound('Game not found')

  if game.created_by != player:
    raise NotAuthorized('Only the creator can start the game')

  can_start, errors = await DbUtils.can_start_game(game, player)
  if not can_start:
    raise InvalidGameState(errors)

  await DbUtils.start_game(game)

  game_state = await DbUtils.get_game_state(game_id)

  await consumer.channel_layer.group_send(
    consumer.room_group_name,
    {
      'type': 'game_started',
      'data': game_state
    }
  )
