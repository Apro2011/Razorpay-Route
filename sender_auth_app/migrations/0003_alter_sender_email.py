# Generated by Django 5.0 on 2023-12-28 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sender_auth_app', '0002_sender_password2_alter_sender_first_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sender',
            name='email',
            field=models.EmailField(blank=True, max_length=254, unique=True),
        ),
    ]