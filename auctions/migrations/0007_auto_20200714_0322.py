# Generated by Django 3.0.8 on 2020-07-13 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_auto_20200713_2332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionlisting',
            name='productName',
            field=models.CharField(max_length=120),
        ),
    ]
