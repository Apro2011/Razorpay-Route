# Generated by Django 4.2.7 on 2023-12-16 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reciever',
            name='group_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
