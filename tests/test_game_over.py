from django.test import SimpleTestCase
from unittest.mock import MagicMock

from game.models import Game
from game.game_over import check_game_over

def make_game(active_players):
  game = MagicMock()
  game.state = Game.GameState.PLAYING
  game.game_players.filter.return_value.select_related.return_value = active_players
  return game

def make_player(username):
  p = MagicMock()
  p.player.user.username = username
  return p

class CheckGameOverTests(SimpleTestCase):
  def test_game_state_not_playing(self):
    game = Game(id=1)
    self.assertIsNone(check_game_over(game))

  def test_multiple_active_players(self):
    p1 = make_player("p1")
    p2 = make_player("p2")
    g = make_game([p1, p2])
    result = check_game_over(g)
    self.assertIsNone(result)
    g.save.assert_not_called()
    

  def test_one_active_player_wins(self):
    p1 = make_player("p1")
    g1 = make_game([p1])
    result = check_game_over(g1)
    self.assertEqual(g1.state, Game.GameState.FINISHED)
    self.assertEqual(result, {'game_ended': True, 'winner': 'p1' })

  def test_no_active_players(self):
    result = check_game_over(make_game([]))
    self.assertEqual(result, {'game_ended': True, 'winner': None})
