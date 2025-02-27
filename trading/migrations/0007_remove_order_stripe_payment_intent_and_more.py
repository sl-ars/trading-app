# Generated by Django 5.1.6 on 2025-02-26 17:21

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0006_remove_order_order_type_remove_transaction_status_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='stripe_payment_intent',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='payment_intent_id',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='payment_method',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='payment_status',
        ),
        migrations.AddField(
            model_name='transaction',
            name='status_from',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='status_to',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaction',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed'), ('canceled', 'Canceled'), ('shipped', 'Shipped')], default='pending', max_length=10),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='trading.order'),
        ),
    ]
