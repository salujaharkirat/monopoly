from events import EventBus
from db_utils import DbUtils

@EventBus.subscribe('start_game')
async def handle_start_game(consumer, data: dict):
  try:
    game_id = data.get('game_id')
    player = await DbUtils.get_player(data.get('user'))
    game = await DbUtils.get_game(game_id)

    if not player:
        await consumer.send_error("Player not found")
        return
    
    if not game:
        await consumer.send_error("Game not found")
        return
    

    if game.created_by != player:
        await consumer.send_error("Only creater can start the game")
        return
    
    can_start, errors = await DbUtils.can_start_game(game, player)
    if not can_start:
        await consumer.send_error("".join(errors))
        return
    
    await DbUtils.start_game(game)

    game_state = await DbUtils.get_game_state(game_id)
    
    await consumer.broadcast_game_state(game_state)
      
  except Exception as e:
    await consumer.send_error(str(e))