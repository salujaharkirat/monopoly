from django.test import SimpleTestCase
from unittest.mock import patch

from game.bank import transfer
from game.models import GamePlayer

class BankTransferTests(SimpleTestCase):
  def test_empty_amount(self):
    self.assertIsNone(transfer(None, None, 0))

  @patch.object(GamePlayer.objects, 'filter')
  def test_from_player_money_deducted(self, mock_filter):
    from_player = GamePlayer(id=1, money=500)
    transfer(from_player, None, 100)
    mock_filter.assert_called_once_with(id=1)
    mock_filter.return_value.update.assert_called_once()
    self.assertEqual(from_player.money, 400)

  @patch.object(GamePlayer.objects, 'filter')
  def test_to_player_money_received(self, mock_filter):
    to_player = GamePlayer(id=1, money=500)
    transfer(None, to_player, 100)
    mock_filter.assert_called_once_with(id=1)
    mock_filter.return_value.update.assert_called_once()
    self.assertEqual(to_player.money, 600)