# Generated by Django 2.1.3 on 2018-12-29 23:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_sandboxplayergroup_removed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='player_group',
        ),
    ]