# Generated by Django 5.0.1 on 2024-03-05 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_alter_user_options_alter_user_managers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='contact_no',
            field=models.IntegerField(null=True),
        ),
    ]
