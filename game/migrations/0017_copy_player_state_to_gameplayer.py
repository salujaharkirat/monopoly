from django.db import migrations


def copy_player_state_to_gameplayer(apps, schema_editor):
  Game = apps.get_model('game', 'Game')
  Player = apps.get_model('game', 'Player')
  GamePlayer = apps.get_model('game', 'GamePlayer')

  # `Game.players.through` is still the old, implicit M2M join table at this
  # point in migration history - 0018 is what repoints it to `GamePlayer`.
  OldMembership = Game.players.through

  for row in OldMembership.objects.all():
    player = Player.objects.get(pk=row.player_id)
    GamePlayer.objects.create(
      game_id=row.game_id,
      player_id=row.player_id,
      money=player.money,
      position=player.position,
      is_in_jail=player.is_in_jail,
      get_out_of_jail_cards=player.get_out_of_jail_cards,
      doubles_count=player.doubles_count,
      has_rolled=player.has_rolled,
      is_active=player.is_active,
    )


class Migration(migrations.Migration):
    """
    Step 2 of 4: populate `GamePlayer` from the current (game, player)
    memberships and each account's current state.

    Caveat, worth knowing if old data is ever inspected: `Player` only ever
    held one snapshot of money/position/etc, so an account that previously
    played and finished an EARLIER game has no recoverable per-game history
    for that old game - this was already true before this migration (the
    single `Player` row was always overwritten the next time a game started
    for that account), so nothing is newly lost. Only the (game, player)
    pair for a currently WAITING/PLAYING game gets a meaningful snapshot;
    older, already-finished games get whatever was left on `Player`, which
    was never meaningful gameplay state and isn't relied on anywhere.

    Irreversible by design - there's nothing to roll `GamePlayer` rows back
    into once `Player` no longer holds these fields (see 0019).
    """

    dependencies = [
        ('game', '0016_gameplayer'),
    ]

    operations = [
        migrations.RunPython(copy_player_state_to_gameplayer, migrations.RunPython.noop),
    ]
