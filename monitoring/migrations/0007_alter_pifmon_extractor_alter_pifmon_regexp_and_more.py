# Generated by Django 4.0.4 on 2022-05-30 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0006_pifmon_sites'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pifmon',
            name='extractor',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='pifmon',
            name='regexp',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AlterField(
            model_name='pifmon',
            name='selector',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
