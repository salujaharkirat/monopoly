from django.test import SimpleTestCase
from unittest.mock import patch

from game.models import GamePlayer
from game.bankruptcy import has_sufficient_amount, mark_bankrupt, settle_debt


class BankruptcyTests(SimpleTestCase):
  def test_sufficient_amount(self):
    me = GamePlayer(id=1, money=1500)
    self.assertTrue(has_sufficient_amount(me, 0))

  def test_not_sufficient_amount(self):
    me = GamePlayer(id=1, money=100)
    self.assertFalse(has_sufficient_amount(me, 200))

  @patch.object(GamePlayer, 'save')
  def test_mark_bankrupt_active_player(self, mock_save):
    me = GamePlayer(id=1)
    self.assertTrue(me.is_active)
    mark_bankrupt(me)
    mock_save.assert_called_once()
    self.assertFalse(me.is_active)

  @patch('game.bankruptcy.mark_bankrupt')
  @patch('game.bank.transfer')
  @patch('game.bankruptcy.has_sufficient_amount')
  def test_amount_less_than_player_money(self, mock_has_sufficient_amount, mock_transfer, mock_mark_bankrupt):

    mock_has_sufficient_amount.return_value = True
    mock_transfer.return_value = None
    mock_mark_bankrupt.returnValue = None

    me = GamePlayer(id=1, money=200)
    res = settle_debt(me, None, 100)
    self.assertFalse(res["is_bankrupt"])
    self.assertEqual(res["paid_amount"], 100)

  @patch('game.bankruptcy.go_bankrupt')
  @patch('game.bank.transfer')
  @patch('game.bankruptcy.has_sufficient_amount')
  def test_amount_more_than_player_money(self, mock_has_sufficient_amount, mock_transfer, mock_go_bankrupt):

    mock_has_sufficient_amount.return_value = False
    mock_transfer.return_value = None

    me = GamePlayer(id=1, money=50)
    res = settle_debt(me, None, 100)
    self.assertTrue(res["is_bankrupt"], True)
    self.assertEqual(res["paid_amount"], 50)
    mock_go_bankrupt.assert_called_once_with(me, None)

  @patch('game.bankruptcy.go_bankrupt')
  @patch('game.bank.transfer')
  @patch('game.bankruptcy.has_sufficient_amount')
  def test_bankrupt_to_a_player_passes_creditor(self, mock_has_sufficient_amount, mock_transfer, mock_go_bankrupt):
    mock_has_sufficient_amount.return_value = False

    me = GamePlayer(id=1, money=50)
    creditor = GamePlayer(id=2, money=500)
    settle_debt(me, creditor, 100)
    mock_go_bankrupt.assert_called_once_with(me, creditor)

  @patch.object(GamePlayer, 'save')
  def test_mark_bankrupt(self, mock_save):
    me = GamePlayer(id=1)
    mark_bankrupt(me)
    mock_save.assert_called_once()
    self.assertFalse(me.is_active)
    mock_save.reset_mock()
    mark_bankrupt(me)
    mock_save.assert_not_called()
    