# Generated by Django 2.1.3 on 2018-11-27 10:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_remove_sandboxplayer_wager'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sandboxplayer',
            name='game',
        ),
        migrations.RemoveField(
            model_name='sandboxplayer',
            name='player_group',
        ),
    ]
