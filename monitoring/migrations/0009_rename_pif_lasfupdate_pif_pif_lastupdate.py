# Generated by Django 4.0.4 on 2022-05-30 16:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0008_checklog_rtype_rule_delete_formsmon_delete_pifmon_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pif',
            old_name='pif_lasfupdate',
            new_name='pif_lastupdate',
        ),
    ]