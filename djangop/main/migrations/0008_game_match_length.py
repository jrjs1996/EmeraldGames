# Generated by Django 2.1.3 on 2018-12-03 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20181129_0501'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='match_length',
            field=models.IntegerField(default=10),
        ),
    ]
