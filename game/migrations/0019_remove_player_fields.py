from django.db import migrations


class Migration(migrations.Migration):
    """
    Step 4 of 4: drop the per-game fields from `Player` now that `GamePlayer`
    (populated in 0017) is the source of truth for them.
    """

    dependencies = [
        ('game', '0018_game_players_through'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='doubles_count',
        ),
        migrations.RemoveField(
            model_name='player',
            name='get_out_of_jail_cards',
        ),
        migrations.RemoveField(
            model_name='player',
            name='has_rolled',
        ),
        migrations.RemoveField(
            model_name='player',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='player',
            name='is_in_jail',
        ),
        migrations.RemoveField(
            model_name='player',
            name='money',
        ),
        migrations.RemoveField(
            model_name='player',
            name='position',
        ),
    ]
