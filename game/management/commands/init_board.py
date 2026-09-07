from django.core.management.base import BaseCommand, CommandError

from game.board_data import BOARD_SQUARES
from game.enums import SquareType
from game.models import Square, ColorGroup

COLORS = {
  'brown': '#8B4513',
  'light_blue': '#87CEEB',
  'pink': '#FF69B4',
  'orange': '#FF8C00',
  'red': '#FF0000',
  'yellow': '#FFD700',
  'green': '#00FF00',
  'dark_blue': '#00008B',
  'railroad': '#808080',
  'utility': '#FFFF00',
}

OWNABLE_TYPES = {SquareType.PROPERTY, SquareType.RAIL_ROAD, SquareType.UTILITY}

BOARD_SIZE = 40


class Command(BaseCommand):
  help = 'Initialize the Monopoly board'

  def handle(self, *args, **options):
    color_groups = {}

    for name, color_code in COLORS.items():
      group, _created = ColorGroup.objects.get_or_create(
        name=name,
        defaults={'color_code': color_code}
      )
      color_groups[name] = group

    for square_data in BOARD_SQUARES:
      color_group = None
      if square_data.get('color'):
        color_group = color_groups.get(square_data['color'])

      Square.objects.update_or_create(
        position=square_data['id'],
        defaults={
          'name': square_data.get('name'),
          'square_type': square_data.get('type'),
          'color_group': color_group,
          'price': square_data.get('price'),
          'rent': square_data.get('rent'),
          'tax_amount': square_data.get('amount'),
          'house_cost': square_data.get('house_cost'),
        }
      )

    self.validate_board()
    self.stdout.write(self.style.SUCCESS(f'Board initialized ({BOARD_SIZE} squares)'))

  def validate_board(self):
    """
    Validate the seeded board
    """
    errors = []

    count = Square.objects.count()
    if count != BOARD_SIZE:
      errors.append(f'Expected {BOARD_SIZE} squares, found {count}')

    missing = set(range(BOARD_SIZE)) - set(
      Square.objects.values_list('position', flat=True)
    )
    if missing:
      errors.append(f'Missing board positions: {sorted(missing)}')

    for square in Square.objects.all().order_by('position'):
      if square.square_type in OWNABLE_TYPES and square.price is None:
        errors.append(f'{square.position} {square.name}: ownable but has no price')

      if square.square_type == SquareType.PROPERTY:
        if square.house_cost is None:
          errors.append(f'{square.position} {square.name}: property has no house_cost')
        if square.rent is None:
          errors.append(f'{square.position} {square.name}: property has no rent')
        if square.color_group is None:
          errors.append(f'{square.position} {square.name}: property has no color group')

      if square.square_type == SquareType.TAX and square.tax_amount is None:
        errors.append(f'{square.position} {square.name}: tax square has no tax_amount')

    if errors:
      raise CommandError(
        'Board validation failed:\n  ' + '\n  '.join(errors)
      )
