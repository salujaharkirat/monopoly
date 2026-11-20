from django.test import SimpleTestCase

from unittest.mock import MagicMock

from game.models import Game
from game.enums import SquareType
from game.rent_calculator import RentCalculator


def make_game():
  game = MagicMock()
  game.state = Game.GameState.PLAYING
  return game

def make_property_square():
  square = MagicMock()
  square.position = 11
  square.square_type = SquareType.PROPERTY
  square.price = 400
  square.rent = 50
  return square

def make_property():
  property = MagicMock()
  property.is_mortgaged = False
  return property



class RentCalculatorTests(SimpleTestCase):
  def test_empty_square(self):
    game = make_game()
    property = make_property()
    property.square = None

    self.assertEqual(RentCalculator.calculate_rent(game, property, 0), 0)

  def test_property_mortaged(self):
    game = make_game()
    property = make_property()
    property.square = make_property_square()
    property.is_mortgaged = True

    self.assertEqual(RentCalculator.calculate_rent(game, property, 0), 0)

  def test_property_rent_no_houses(self):
    game = make_game()
    property = make_property()
    property.square = make_property_square()

    self.assertEqual(RentCalculator.calculate_rent(game, property, 0), 50)

  def test_property_rent_with_houses(self):
    game = make_game()
    property = make_property()
    property.square = make_property_square()
    property.houses = 3

    self.assertEqual(RentCalculator.calculate_rent(game, property, 0), 1750)