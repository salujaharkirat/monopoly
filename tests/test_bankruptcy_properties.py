from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from game.models import Game, GamePlayer, Property
from game.service import GameService
from game.strategies.card_strategy import PayEachPlayerStrategy

INCOME_TAX = 4
BALTIC = 3
READING = 5
PARK_PLACE = 37
BOARDWALK = 39


class BankruptcyPropertiesTests(TestCase):
  """
  What happens to a bankrupt player's properties - and that they stop
  collecting rent on them. Plays real rolls with scripted dice.
  """

  @classmethod
  def setUpTestData(cls):
    call_command('init_board', verbosity=0)

  def start(self, *names):
    users = [User.objects.create_user(n, password='pw') for n in names]
    self.players = [u.monopoly_player for u in users]
    self.game = Game.objects.create(created_by=self.players[0], max_players=4)
    for player in self.players:
      GamePlayer.objects.create(game=self.game, player=player)
    result = GameService.start_game(self.game.id, self.players[0].id)
    self.assertTrue(result['success'], result)

  def gp(self, player):
    return GamePlayer.objects.get(game=self.game, player=player)

  def prop(self, position):
    return Property.objects.get(game=self.game, square__position=position)

  def own(self, player, *positions, houses=0, mortgaged=False):
    Property.objects.filter(game=self.game, square__position__in=positions).update(
      owner=player, houses=houses, is_mortgaged=mortgaged
    )

  def set_money(self, player, money, position=None):
    fields = {'money': money}
    if position is not None:
      fields['position'] = position
    GamePlayer.objects.filter(game=self.game, player=player).update(**fields)

  def roll(self, player, die1, die2):
    with patch('game.service.random.randint', side_effect=[die1, die2]):
      return GameService.roll_dice(self.game.id, player.id)

  def test_bankrupt_to_the_bank_returns_properties_to_the_market(self):
    self.start('a', 'b', 'c')
    a, b, c = self.players
    self.own(a, BOARDWALK, PARK_PLACE, houses=2)
    self.own(a, READING, mortgaged=True)
    self.own(b, BALTIC, houses=1)
    self.set_money(a, 100)

    result = self.roll(a, 1, 3)  # Income Tax, $200 due

    self.assertTrue(result['is_bankrupt'])
    for position in (BOARDWALK, PARK_PLACE, READING):
      prop = self.prop(position)
      self.assertIsNone(prop.owner, position)
      self.assertEqual(prop.houses, 0, position)
      self.assertFalse(prop.is_mortgaged, position)

    # Someone else's property is left alone.
    self.assertEqual(self.prop(BALTIC).owner, b)
    self.assertEqual(self.prop(BALTIC).houses, 1)

  def test_bankrupt_to_a_player_hands_properties_to_that_player(self):
    self.start('a', 'b', 'c')
    a, b, c = self.players
    self.own(c, BALTIC, houses=5)  # hotel: rent 4 x 60 = 240
    self.own(a, BOARDWALK, PARK_PLACE, houses=2)
    self.own(a, READING, mortgaged=True)
    self.set_money(a, 100)

    result = self.roll(a, 1, 2)  # Baltic Avenue

    self.assertTrue(result['is_bankrupt'])
    self.assertFalse(self.gp(a).is_active)
    for position in (BOARDWALK, PARK_PLACE, READING):
      self.assertEqual(self.prop(position).owner, c, position)
      self.assertEqual(self.prop(position).houses, 0, position)

    # The mortgage travels with the property.
    self.assertTrue(self.prop(READING).is_mortgaged)
    self.assertEqual(self.gp(c).money, 2100)

  def test_bankrupt_player_no_longer_collects_rent(self):
    self.start('a', 'b', 'c')
    a, b, c = self.players
    self.own(a, BOARDWALK)
    self.own(c, BALTIC, houses=5)
    self.set_money(a, 100)
    self.roll(a, 1, 2)  # a goes bankrupt to c, Boardwalk now c's

    self.set_money(b, 2000, position=28)
    result = self.roll(b, 5, 6)  # b lands on Boardwalk

    self.assertEqual(result['data']['square_result']['rent_paid'], 50)
    self.assertEqual(self.gp(a).money, 0)
    self.assertEqual(self.gp(c).money, 2000 + 100 + 50)

  def test_two_player_game_ends_with_the_winner_owning_everything(self):
    self.start('a', 'b')
    a, b = self.players
    self.own(a, BOARDWALK)
    self.own(b, BALTIC, houses=5)
    self.set_money(a, 100)

    result = self.roll(a, 1, 2)

    self.assertTrue(result['game_ended'])
    self.assertEqual(result['winner'], 'b')
    self.assertEqual(self.game.__class__.objects.get(id=self.game.id).state, Game.GameState.FINISHED)
    self.assertEqual(self.prop(BOARDWALK).owner, b)

  def test_paying_every_player_bankrupt_returns_properties_to_the_bank(self):
    self.start('a', 'b', 'c')
    a, b, c = self.players
    self.own(a, BOARDWALK, houses=1)
    self.set_money(a, 10)
    card = {'amount': 50}
    square = self.prop(7).square  # any square; the strategy ignores it

    result = PayEachPlayerStrategy().execute(self.gp(a), square, self.game, card)

    self.assertTrue(result['is_bankrupt'])
    self.assertFalse(self.gp(a).is_active)
    self.assertIsNone(self.prop(BOARDWALK).owner)
    self.assertEqual(self.prop(BOARDWALK).houses, 0)

  def test_bankrupt_to_bank_by_card_or_bail_also_forfeits(self):
    self.start('a', 'b', 'c')
    a, b, c = self.players
    self.own(a, BOARDWALK)
    self.set_money(a, 10, position=10)
    GamePlayer.objects.filter(game=self.game, player=a).update(is_in_jail=True)

    result = GameService.pay_bail(self.game.id, a.id)  # $50 bail, $10 held

    self.assertFalse(result['success'])
    self.assertFalse(self.gp(a).is_active)
    self.assertIsNone(self.prop(BOARDWALK).owner)
