# Generated by Django 3.0.8 on 2020-07-16 23:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_auto_20200714_0322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionlisting',
            name='datetime',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
