# Generated by Django 5.0.9 on 2024-11-07 03:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appln', '0014_alter_upload_file_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upload',
            name='request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uploads', to='appln.request', unique=True),
        ),
    ]
