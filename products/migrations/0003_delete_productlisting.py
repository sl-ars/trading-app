# Generated by Django 5.1.6 on 2025-02-24 17:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_remove_productlisting_category_and_more'),
        ('trading', '0005_alter_order_product'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProductListing',
        ),
    ]
