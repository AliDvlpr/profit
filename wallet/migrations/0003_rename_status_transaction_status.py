# Generated by Django 4.2.4 on 2023-08-12 07:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0002_transaction'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='STATUS',
            new_name='status',
        ),
    ]
