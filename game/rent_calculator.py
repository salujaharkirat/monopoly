from game.enums import SquareType
from game.models import Game, Property, Square

# Rent multipliers indexed by house count. 5 houses is a hotel.
RENT_MULTIPLIERS = {0: 1, 1: 5, 2: 15, 3: 35, 4: 50, 5: 60}

RAILROAD_BASE_RENT = 25


class RentCalculator:
  @staticmethod
  def calculate_rent(game: Game, property: Property, dice_roll: int = 0):
    square = property.square

    if not square:
      return 0

    if property.is_mortgaged:
      return 0

    if square.square_type == SquareType.PROPERTY:
      return RentCalculator._calculate_property_rent(square, property)

    if square.square_type == SquareType.RAIL_ROAD:
      return RentCalculator._calculate_rail_road_rent(game, property)

    if square.square_type == SquareType.UTILITY:
      return RentCalculator._calculate_utility_rent(game, property, dice_roll)

    return 0

  @staticmethod
  def _calculate_property_rent(square: Square, property: Property):
    base_rent = square.rent or 0
    multiplier = RENT_MULTIPLIERS.get(property.houses, 1)
    return base_rent * multiplier

  @staticmethod
  def _count_owned_in_type(game: Game, property: Property, square_type):
    """
    Count co-owned properties for railroad and ulitilities
    """
    if property.owner is None:
      return 0

    return Property.objects.filter(
      owner=property.owner,
      square__square_type=square_type,
      game=game,
      is_mortgaged=False,
    ).count()

  @staticmethod
  def _calculate_rail_road_rent(game: Game, property: Property):
    owned = RentCalculator._count_owned_in_type(game, property, SquareType.RAIL_ROAD)
    if owned <= 0:
      return RAILROAD_BASE_RENT
    return RAILROAD_BASE_RENT * (2 ** (owned - 1))

  @staticmethod
  def _calculate_utility_rent(game: Game, property: Property, dice_roll: int):
    owned = RentCalculator._count_owned_in_type(game, property, SquareType.UTILITY)
    multiplier = 4 if owned <= 1 else 10
    return dice_roll * multiplier