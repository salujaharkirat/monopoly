from django.test import SimpleTestCase

from unittest.mock import MagicMock, patch

from game.models import Game, Property
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

def make_railroad_square():
  square = MagicMock()
  square.position = 5
  square.square_type = SquareType.RAIL_ROAD
  square.price = 400
  square.rent = 50
  return square

def make_utility_square():
  square = MagicMock()
  square.position = 12
  square.square_type = SquareType.UTILITY
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


  def test_no_square_type_match(self):
    game = make_game()
    property = make_property()
    property.square.square_type = "Random"

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

  @patch('game.rent_calculator.RentCalculator._count_owned_in_type')
  def test_rail_road_rent_no_co_owned_properties(self, mock_owned_in_type_count):
    game = make_game()
    property = make_property()
    property.square = make_railroad_square()
    mock_owned_in_type_count.return_value = 0

    self.assertEqual(RentCalculator.calculate_rent(game, property, 0), 25)

  @patch('game.rent_calculator.RentCalculator._count_owned_in_type')
  def test_rail_road_rent_co_owned_properties(self, mock_owned_in_type_count):
    game = make_game()
    property = make_property()
    property.square = make_railroad_square()
    mock_owned_in_type_count.return_value = 2

    self.assertEqual(RentCalculator.calculate_rent(game, property, 0), 50)

  @patch('game.rent_calculator.RentCalculator._count_owned_in_type')
  def test_rail_utility_one_co_owned_properties(self, mock_owned_in_type_count):
    game = make_game()
    property = make_property()
    property.square = make_utility_square()
    mock_owned_in_type_count.return_value = 1

    self.assertEqual(RentCalculator.calculate_rent(game, property, 4), 16)

  @patch('game.rent_calculator.RentCalculator._count_owned_in_type')
  def test_rail_utility_mulitple_co_owned_properties(self, mock_owned_in_type_count):
    game = make_game()
    property = make_property()
    property.square = make_utility_square()
    mock_owned_in_type_count.return_value = 3

    self.assertEqual(RentCalculator.calculate_rent(game, property, 4), 40)
  

  @patch.object(Property.objects, 'filter')
  def test_count_owned_in_type_not_owner(self, mock_property_filter):
    game = make_game()
    property = make_property()
    property.square = make_railroad_square()
    property.owner = None


    mock_property_filter.return_value.count.return_value = 2

    self.assertEqual(RentCalculator._count_owned_in_type(game, property, SquareType.RAIL_ROAD), 0)

  @patch.object(Property.objects, 'filter')
  def test_count_owned_in_type_owner(self, mock_property_filter):
    game = make_game()
    property = make_property()
    property.square = make_railroad_square()


    mock_property_filter.return_value.count.return_value = 2

    self.assertEqual(RentCalculator._count_owned_in_type(game, property, SquareType.RAIL_ROAD), 2)

  