# Generated by Django 2.1.3 on 2018-11-27 10:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_remove_sandboxplayer_in_game'),
    ]

    operations = [
        migrations.AddField(
            model_name='sandboxplayer',
            name='game',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='main.Game'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sandboxplayer',
            name='player_group',
            field=models.ForeignKey(blank=True, db_constraint=False, default=1, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='main.SandboxPlayerGroup'),
        ),
    ]