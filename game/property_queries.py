"""
Shared queries over a color group's properties.

`build_house`/`sell_house` (ownership) and `can_evenly_construct`/
`can_evenly_sell` (house counts) each had their own hand-copied version of
these - the two pairs already had to be kept in sync by hand once this
session. One definition each, used by both sides.
"""

from game.models import Property


def owns_entire_group(player, color_group, game):
  """Whether `player` owns every property in `color_group` for `game`."""
  total = Property.objects.filter(square__color_group=color_group, game=game).count()
  owned = Property.objects.filter(
    owner=player, square__color_group=color_group, game=game
  ).count()
  return total == owned


def other_house_counts(property, color_group, game):
  """House counts for every OTHER property in `property`'s color group."""
  return list(
    Property.objects.filter(square__color_group=color_group, game=game)
    .exclude(id=property.id)
    .values_list('houses', flat=True)
  )
