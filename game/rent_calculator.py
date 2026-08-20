from game.enums import SquareType
from game.models import Game, Property, Square

class RentCalculator:
  @staticmethod
  def calculate_rent(game: Game, property: Property, dice_roll: int = 0):
    square = property.square

    if not square:
      return 0

    if property.is_mortgaged:
      return 0

    if square.square_type == SquareType.PROPERTY:
      return RentCalculator._calculate_property_rent(square, game, property)

    if square.square_type == SquareType.RAIL_ROAD:
      return RentCalculator._calculate_rail_road_rent(game, property)

    if square.square_type == SquareType.UTILITY:
      return RentCalculator._calculate_utility_rent(game, property, dice_roll)

    return 0

  @staticmethod
  def _calculate_property_rent(square: Square, property: Property):
    houses = property.houses
    base_rent = square.rent or 0
    rent_tiers = {
      0: base_rent,
      1: 5 * base_rent,
      2: 15 * base_rent,
      3: 35 * base_rent,
      4: 50 * base_rent,
      5: 60 * base_rent
    }

    return rent_tiers.get(houses)

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

  @staticmethod
  def _calculate_utility_rent(game: Game, property: Property, dice_roll: int):
    number_of_properties = Property.objects.filter(
      owner = property.owner,
      square_square_type = Square.SquareType.UTILITY,
      game=game,
    ).count()

    if number_of_properties == 1:
      return dice_roll * 4

    return dice_roll * 10
  