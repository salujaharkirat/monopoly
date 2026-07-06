from django.core.management.base import BaseCommand
from game.models import Square, ColorGroup
from game.board_data import BOARD_SQUARES

class Command(BaseCommand):
  help = 'Initialize the Monopoly board'

  def handle(self, *args, **options):
    color_groups = {}
    colors = {
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

    for name, color_code in colors.items():
      group, created = ColorGroup.objects.get_or_create(
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
        defaults = {
          'name': square_data.get('name'),
          'square_type': square_data.get('type').upper(),
          'color_group': color_group,
          'price': square_data.get('price'),
          'rent': square_data.get('rent'),
          'tax_amount': square_data.get('amount')
        }
      )

    self.stdout.write(self.style.SUCCESS('Board initialized'))