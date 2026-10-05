from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Step 3 of 4: repoint `Game.players` to use `GamePlayer` as its `through`
    model.

    Django's schema editor refuses to `AlterField` an M2M into or out of a
    `through=` model directly ("you cannot alter to or from M2M fields, or
    add or remove through= on M2M fields") - confirmed by actually trying it
    and hitting that `ValueError` while writing this migration - so this has
    to be a drop-and-recreate of the field itself rather than a single
    `AlterField`. The underlying membership data is not lost: 0017 already
    copied every (game, player) pairing - along with each account's state -
    into `GamePlayer` before this runs, so dropping the old implicit join
    table here discards nothing that still matters.
    """

    dependencies = [
        ('game', '0017_copy_player_state_to_gameplayer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='players',
        ),
        migrations.AddField(
            model_name='game',
            name='players',
            field=models.ManyToManyField(related_name='games', through='game.GamePlayer', to='game.player', verbose_name='list of players'),
        ),
    ]
