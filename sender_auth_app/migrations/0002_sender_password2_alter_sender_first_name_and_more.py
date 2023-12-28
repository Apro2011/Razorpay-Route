# Generated by Django 5.0 on 2023-12-28 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sender_auth_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sender',
            name='password2',
            field=models.CharField(blank=True, max_length=16),
        ),
        migrations.AlterField(
            model_name='sender',
            name='first_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='sender',
            name='last_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='sender',
            name='password',
            field=models.CharField(blank=True, max_length=16),
        ),
    ]
