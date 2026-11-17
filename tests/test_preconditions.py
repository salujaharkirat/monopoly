from django.test import SimpleTestCase
from unittest.mock import patch

from game.exceptions import NotYourTurn
from game.models import Game, GamePlayer
from game.preconditions import require_playing, require_current_player, \
require_active, require_in_jail, require_not_in_jail, require_not_rolled
from game.exceptions import InvalidGameState, PlayerBankrupt, NotInJail, \
PlayerInJail, InvalidAction

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

class RequireCurrentPlayerTests(SimpleTestCase):
  def setUp(self):
    self.game = Game(state=Game.GameState.PLAYING)
  
  @patch('game.preconditions.turn_order.get_current_player')
  def test_passes_current_player_turn(self, get_current_player):
    me = GamePlayer(id=1)
    get_current_player.return_value = me

    self.assertIsNone(require_current_player(self.game, me))


  @patch('game.preconditions.turn_order.get_current_player')
  def test_raises_when_it_is_someone_elses_turn(self, get_current_player):
    me = GamePlayer(id=1)
    get_current_player.return_value = GamePlayer(id=2)

    with self.assertRaises(NotYourTurn):
      require_current_player(self.game, me)

  @patch('game.preconditions.turn_order.get_current_player')
  def test_raises_when_game_has_no_players(self, get_current_player):
    get_current_player.return_value = None

    with self.assertRaises(NotYourTurn):
      require_current_player(self.game, GamePlayer(id=1))

class RequireActiveTests(SimpleTestCase):
  def test_player_is_active(self):
    me = GamePlayer(id=1)
    self.assertIsNone(require_active(me))

  def test_player_is_not_active(self):
    me = GamePlayer(id=1, is_active=False)

    with self.assertRaises(PlayerBankrupt):
      require_active(me)

class RequireInJailTests(SimpleTestCase):
  def test_player_in_jail(self):
    me = GamePlayer(id=1)
    with self.assertRaises(NotInJail):
      require_in_jail(me)

  def test_player_not_in_jail(self):
    me = GamePlayer(id=1, is_in_jail=True)
    self.assertIsNone(require_in_jail(me))

class RequireNotInJailTests(SimpleTestCase):
  def test_player_not_in_jail(self):
    me = GamePlayer(id=1, is_in_jail=True)
    with self.assertRaises(PlayerInJail):
      require_not_in_jail(me)

  def test_player_in_jail(self):
    me = GamePlayer(id=1)
    self.assertIsNone(require_not_in_jail(me))

class RequiredNotRolledTests(SimpleTestCase):
  def test_player_has_rolled_raises(self):
    me = GamePlayer(id=1, has_rolled=True)
    with self.assertRaises(InvalidAction):
      require_not_rolled(me)
