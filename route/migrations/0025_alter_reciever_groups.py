# Generated by Django 5.0.1 on 2024-01-05 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('route', '0024_alter_recieversgroup_photo_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reciever',
            name='groups',
            field=models.ManyToManyField(related_name='reciever_recievergroups', to='route.recieversgroup'),
        ),
    ]