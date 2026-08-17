from game.enums import SquareType
from models import Game, Property, Square

class RentCalculator:
  @staticmethod
  def calculate_rent(game: Game, property: Property):
    square = property.square

    if not square:
      return 0

    if property.is_mortgaged:
      return 0

    if square.square_type == SquareType.PROPERTY:
      return RentCalculator._calculate_property_rent(square)

    if square.square_type == SquareType.RAIL_ROAD:
      return RentCalculator._calculate_rail_road_rent(game, property)

    return 0

  @staticmethod
  def _calculate_property_rent(square: Square):
    return square.rent or 0 

  @staticmethod
  def _calculate_rail_road_rent(game: Game, property: Property):
    baseRent = 25
    number_of_properties = Property.objects.filter(
      owner = property.owner,
      square__square_type = Square.SquareType.RAILROAD,
      game = game,
    ).count()

    if number_of_properties > 0:
      return baseRent * (number_of_properties)

    return baseRent
  