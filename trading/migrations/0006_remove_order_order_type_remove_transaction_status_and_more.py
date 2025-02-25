# Generated by Django 5.1.6 on 2025-02-24 19:25

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_delete_productlisting'),
        ('trading', '0005_alter_order_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='order_type',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='status',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='transaction_amount',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='transaction_date',
        ),
        migrations.AddField(
            model_name='order',
            name='stripe_payment_intent',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='created_at',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='transaction',
            name='payment_intent_id',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='payment_method',
            field=models.CharField(choices=[('card', 'Card'), ('cash', 'Cash')], default='card', max_length=50),
        ),
        migrations.AddField(
            model_name='transaction',
            name='payment_status',
            field=models.CharField(choices=[('paid', 'Paid'), ('failed', 'Failed')], default='paid', max_length=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='products.product'),
        ),
        migrations.AlterField(
            model_name='order',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed'), ('canceled', 'Canceled')], default='pending', max_length=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
