# Generated by Django 5.0.9 on 2024-10-10 00:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appln', '0002_alter_artist_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artist',
            name='user',
        ),
    ]
