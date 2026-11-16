from django.test import TestCase, SimpleTestCase

from game.models import Game, Player
from game.preconditions import require_playing
from game.exceptions import InvalidGameState

# Create your tests here.

class RequirePlayingTests(SimpleTestCase):
  def test_passes_when_playing(self):
    game = Game(state=Game.GameState.PLAYING)
    self.assertIsNone(require_playing(game))

  def test_raises_when_not_playing(self):
    for state in (Game.GameState.WAITING, Game.GameState.FINISHED, Game.GameState.CANCELLED):
      with self.subTest(state=state):
        game = Game(state=state)
        with self.assertRaises(InvalidGameState):
          require_playing(game)
