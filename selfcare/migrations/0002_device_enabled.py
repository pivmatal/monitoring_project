# Generated by Django 4.0.4 on 2023-02-06 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selfcare', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
    ]