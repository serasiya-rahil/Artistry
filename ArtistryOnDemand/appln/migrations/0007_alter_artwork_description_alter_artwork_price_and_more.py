# Generated by Django 5.0.9 on 2024-10-12 04:13

import appln.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appln', '0006_alter_artist_email_alter_artist_first_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artwork',
            name='description',
            field=models.TextField(validators=[appln.validators.ValidateTitleImpl]),
        ),
        migrations.AlterField(
            model_name='artwork',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[appln.validators.ValidatePriceImpl]),
        ),
        migrations.AlterField(
            model_name='artwork',
            name='title',
            field=models.CharField(max_length=255, validators=[appln.validators.ValidateTitleImpl]),
        ),
    ]
