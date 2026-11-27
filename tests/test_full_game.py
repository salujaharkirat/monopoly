from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from game.models import Game, GamePlayer, Property
from game.service import GameService


class FullGameTests(TestCase):
  """
  One complete two-player game, from lobby to a declared winner.

  Everything goes through the same entry points the real clients use: the
  REST views for create / join / start, and `GameService` for every in-game
  action. Only the dice are scripted (`roll`), so the game is deterministic.
  The script never lands on Chance / Community Chest, whose draw is random.

  Real play would need many laps to drain a $2000 bankroll, so just before the
  final roll `test_two_player_game_to_completion` fast-forwards the loser's
  money with a direct update. That is the only shortcut taken.
  """

  @classmethod
  def setUpTestData(cls):
    # The board is seeded by a management command, not by migrations.
    call_command('init_board', verbosity=0)

  def setUp(self):
    self.alice_user = User.objects.create_user('alice', password='pw')
    self.bob_user = User.objects.create_user('bob', password='pw')
    # The post_save signal creates a Player for every new User.
    self.alice = self.alice_user.monopoly_player
    self.bob = self.bob_user.monopoly_player

  # ---- helpers -----------------------------------------------------------

  def api(self, user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client

  def roll(self, player, die1, die2):
    """
    Roll with scripted dice. `side_effect` is a two-item list, so a roll that
    asks for a third random number fails loudly instead of drifting.
    """
    with patch('game.service.random.randint', side_effect=[die1, die2]):
      return GameService.roll_dice(self.game.id, player.id)

  def gp(self, player):
    return GamePlayer.objects.get(game=self.game, player=player)

  def prop(self, position):
    return Property.objects.select_related('owner').get(
      game=self.game, square__position=position
    )

  def buy(self, player, position):
    result = GameService.buy_property(self.game.id, player.id, self.prop(position).id)
    self.assertTrue(result['success'], result)
    return result

  def build(self, player, position, houses=1):
    result = GameService.build_house(self.game.id, player.id, self.prop(position).id, houses)
    self.assertTrue(result['success'], result)
    return result

  def end_turn(self, player):
    result = GameService.end_turn(self.game.id, player.id)
    self.assertTrue(result['success'], result)
    return result

  def assert_rolled(self, result, to_position, doubles=False, passed_go=False):
    self.assertTrue(result['success'], result)
    dice = result['data']['dice']
    self.assertEqual(dice['new_position'], to_position)
    self.assertEqual(dice['is_doubles'], doubles)
    self.assertEqual(dice['passed_go'], passed_go)

  def assert_money(self, alice, bob):
    self.assertEqual(self.gp(self.alice).money, alice, 'alice money')
    self.assertEqual(self.gp(self.bob).money, bob, 'bob money')

  def assert_owner(self, position, player):
    self.assertEqual(self.prop(position).owner, player)

  # ---- the game ----------------------------------------------------------

  def test_two_player_game_to_completion(self):
    self.start_game()

    # Turn 1
    # alice: 4+5 -> Connecticut Ave (120)
    self.assert_rolled(self.roll(self.alice, 4, 5), 9)
    self.buy(self.alice, 9)
    self.assert_money(1880, 2000)
    self.end_turn(self.alice)

    # bob: 2+3 -> Reading Railroad (200)
    self.assert_rolled(self.roll(self.bob, 2, 3), 5)
    self.buy(self.bob, 5)
    self.assert_money(1880, 1800)
    self.end_turn(self.bob)

    # Turn 2
    # alice: 5+6 -> Free Parking, nothing happens
    result = self.roll(self.alice, 5, 6)
    self.assert_rolled(result, 20)
    self.assertEqual(result['data']['square_result']['name'], 'Free Parking')
    self.end_turn(self.alice)

    # bob: 3+4 -> Electric Company (150)
    self.assert_rolled(self.roll(self.bob, 3, 4), 12)
    self.buy(self.bob, 12)
    self.assert_money(1880, 1650)
    self.end_turn(self.bob)

    # Turn 3
    # alice: 4+5 -> Marvin Gardens (280)
    self.assert_rolled(self.roll(self.alice, 4, 5), 29)
    self.buy(self.alice, 29)
    self.end_turn(self.alice)

    # bob: 1+2 -> Pennsylvania Railroad (200)
    self.assert_rolled(self.roll(self.bob, 1, 2), 15)
    self.buy(self.bob, 15)
    self.assert_money(1600, 1450)
    self.end_turn(self.bob)

    # Turn 4
    # alice: 3+5 -> Park Place (350)
    self.assert_rolled(self.roll(self.alice, 3, 5), 37)
    self.buy(self.alice, 37)
    self.end_turn(self.alice)

    # bob: 4+6 -> B&O Railroad (200); bob now holds three of the four railroads
    self.assert_rolled(self.roll(self.bob, 4, 6), 25)
    self.buy(self.bob, 25)
    self.assert_money(1250, 1250)
    self.end_turn(self.bob)

    # Turn 5
    # alice: doubles 1+1 -> Boardwalk (400), completing the dark blue pair
    result = self.roll(self.alice, 1, 1)
    self.assert_rolled(result, 39, doubles=True)
    self.buy(self.alice, 39)
    self.assert_money(850, 1250)

    # The pair is a monopoly now, so she can build, evenly: one house each.
    self.build(self.alice, 37)
    self.build(self.alice, 39)
    self.assert_money(450, 1250)
    self.assertEqual(self.prop(37).houses, 1)
    self.assertEqual(self.prop(39).houses, 1)

    # Doubles earned another roll in the same turn: 1+3 wraps past GO (+200)
    self.assert_rolled(self.roll(self.alice, 1, 3), 3, passed_go=True)
    self.assert_money(650, 1250)

    # Having now rolled a non-double, a third roll is refused.
    again = self.roll(self.alice, 2, 3)
    self.assertFalse(again['success'])
    self.assertEqual(again['error'], 'InvalidAction')
    self.end_turn(self.alice)

    # bob: doubles 6+6 -> Park Place, one house: rent 35 x 5 = 175
    result = self.roll(self.bob, 6, 6)
    self.assert_rolled(result, 37, doubles=True)
    self.assertEqual(result['data']['square_result']['rent_paid'], 175)
    self.assert_money(825, 1075)

    # then 4+5 wraps past GO (+200) onto Oriental Avenue (100)
    self.assert_rolled(self.roll(self.bob, 4, 5), 6, passed_go=True)
    self.buy(self.bob, 6)
    self.assert_money(825, 1175)
    self.end_turn(self.bob)

    # Turn 6
    # alice: doubles 1+1 -> Reading Railroad, bob owns 3 railroads: 25 x 2^2 = 100
    result = self.roll(self.alice, 1, 1)
    self.assert_rolled(result, 5, doubles=True)
    self.assertEqual(result['data']['square_result']['rent_paid'], 100)
    self.assert_money(725, 1275)

    # then 2+3 -> Jail / Just Visiting, which is not a trip to jail
    result = self.roll(self.alice, 2, 3)
    self.assert_rolled(result, 10)
    self.assertFalse(self.gp(self.alice).is_in_jail)
    self.end_turn(self.alice)

    # bob: 4+5 -> Pennsylvania Railroad, his own, so no rent
    result = self.roll(self.bob, 4, 5)
    self.assert_rolled(result, 15)
    self.assertNotIn('rent_paid', result['data']['square_result'])
    self.end_turn(self.bob)

    # Turn 7
    # alice: second house on each dark blue property
    self.build(self.alice, 37)
    self.build(self.alice, 39)
    self.assert_money(325, 1275)
    self.assertEqual(self.prop(37).houses, 2)
    self.assertEqual(self.prop(39).houses, 2)

    # alice: 1+2 -> States Avenue, which she passes on
    result = self.roll(self.alice, 1, 2)
    self.assert_rolled(result, 13)
    self.assertTrue(result['data']['square_result']['can_buy'])
    self.end_turn(self.alice)

    # bob: 5+6 -> Atlantic Avenue (260)
    self.assert_rolled(self.roll(self.bob, 5, 6), 26)
    self.buy(self.bob, 26)
    self.assert_money(325, 1015)
    self.end_turn(self.bob)

    # Turn 8
    # alice: 3+4 -> Free Parking
    self.assert_rolled(self.roll(self.alice, 3, 4), 20)
    self.end_turn(self.alice)

    # Fast-forward: bob is down to $300, less than the rent about to be due.
    GamePlayer.objects.filter(game=self.game, player=self.bob).update(money=300)
    self.assert_money(325, 300)

    # bob: 5+6 -> Park Place with two houses: rent 35 x 15 = 525, he has 300
    result = self.roll(self.bob, 5, 6)

    self.assertFalse(result['success'])
    self.assertTrue(result['is_bankrupt'])
    self.assertTrue(result['game_ended'])
    self.assertEqual(result['winner'], 'alice')

    # ---- final state ---------------------------------------------------

    self.game.refresh_from_db()
    self.assertEqual(self.game.state, Game.GameState.FINISHED)

    bob = self.gp(self.bob)
    self.assertFalse(bob.is_active)
    self.assertEqual(bob.money, 0)

    # alice collected only what bob had left, not the full 525.
    alice = self.gp(self.alice)
    self.assertTrue(alice.is_active)
    self.assertEqual(alice.money, 625)

    # A finished game accepts no further actions.
    after = GameService.end_turn(self.game.id, self.alice.id)
    self.assertFalse(after['success'])
    self.assertEqual(after['error'], 'InvalidGameState')

  def start_game(self):
    """Lobby: alice creates, bob joins, alice starts. Checks the turn order."""
    alice_api = self.api(self.alice_user)
    bob_api = self.api(self.bob_user)

    response = alice_api.post(
      '/api/games/create/', {'name': 'e2e', 'max_players': 2, 'min_players': 2}, format='json'
    )
    self.assertEqual(response.status_code, 201, response.content)
    self.game = Game.objects.get(id=response.data['id'])
    self.assertEqual(self.game.state, Game.GameState.WAITING)

    # A lobby with one player is not enough.
    early = GameService.start_game(self.game.id, self.alice.id)
    self.assertFalse(early['success'])
    self.assertEqual(early['error'], 'InvalidGameState')

    response = bob_api.post(f'/api/games/{self.game.id}/join/')
    self.assertEqual(response.status_code, 200, response.content)

    # Only the creator may start.
    refused = GameService.start_game(self.game.id, self.bob.id)
    self.assertFalse(refused['success'])
    self.assertEqual(refused['error'], 'NotAuthorized')

    response = alice_api.post(f'/api/games/{self.game.id}/start/')
    self.assertEqual(response.status_code, 200, response.content)

    self.game.refresh_from_db()
    self.assertEqual(self.game.state, Game.GameState.PLAYING)
    self.assertEqual(self.game.current_player_index, 0)

    # Every square got a Property row for this game, all unowned.
    self.assertEqual(Property.objects.filter(game=self.game).count(), 40)
    self.assertFalse(Property.objects.filter(game=self.game, owner__isnull=False).exists())

    for game_player in GamePlayer.objects.filter(game=self.game):
      self.assertEqual(game_player.money, 2000)
      self.assertEqual(game_player.position, 0)

    # Join order is turn order: bob may not jump the queue.
    out_of_turn = GameService.roll_dice(self.game.id, self.bob.id)
    self.assertFalse(out_of_turn['success'])
    self.assertEqual(out_of_turn['error'], 'NotYourTurn')
