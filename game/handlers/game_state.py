
async def handle_game_state(consumer, data: dict):
  try:
    await consumer.send_game_state()
      
  except Exception as e:
    await consumer.send_error(str(e))