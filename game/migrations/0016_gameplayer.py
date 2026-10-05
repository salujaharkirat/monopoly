import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Step 1 of 4 in splitting per-game player state off of `Player` and onto
    a new `GamePlayer` through-model (see 0017-0019). This step only creates
    the new table - `Game.players` and `Player` are untouched here, so the
    data migration in 0017 can still read both the old implicit M2M join
    table and `Player`'s current field values to populate it.
    """

    dependencies = [
        ('game', '0015_player_has_rolled'),
    ]

    operations = [
        migrations.CreateModel(
            name='GamePlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('money', models.IntegerField(default=2000)),
                ('position', models.IntegerField(default=0)),
                ('is_in_jail', models.BooleanField(default=False)),
                ('get_out_of_jail_cards', models.IntegerField(default=0)),
                ('doubles_count', models.IntegerField(default=0)),
                ('has_rolled', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='game_players', to='game.game')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='game_players', to='game.player')),
            ],
            options={
                'ordering': ['id'],
                'unique_together': {('game', 'player')},
            },
        ),
    ]
