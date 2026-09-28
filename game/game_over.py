from game.models import Game


def check_game_over(game):
  """Finish the game if at most one active player remains.

  Call this right after any action that may have deactivated a player
  or removed one from the game.
  """
  if game.state != Game.GameState.PLAYING:
    return None

  active_players = list(game.players.filter(is_active=True))
  if len(active_players) > 1:
    return None

  game.state = Game.GameState.FINISHED
  game.save(update_fields=['state'])

  winner = active_players[0] if active_players else None
  return {
    'game_ended': True,
    'winner': winner.user.username if winner else None,
  }
