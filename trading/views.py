from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
import stripe
from trading.models import Order, Transaction
from products.models import Product, Category
from trading_app.permissions import IsAdmin, IsManager, IsSeller, IsOwnerOrAdmin, IsAdminOrReadOnly
from .forms import OrderForm
from django.conf import settings


# Set Stripe Secret Key
stripe.api_key = settings.STRIPE_SECRET_KEY

def main_page(request):
    """ Main page displaying categories, featured products, and latest listings """
    categories = Category.objects.all()
    featured_products = Product.objects.order_by('?')[:3]
    latest_products = Product.objects.order_by('-created_at')[:3]
    return render(request, 'main_page.html', {
        'categories': categories,
        'featured_products': featured_products,
        'latest_products': latest_products,
    })


@login_required
def order_list(request):
    """ View for displaying all orders of the current user """
    orders = Order.objects.filter(user=request.user).select_related('product')
    return render(request, 'trading/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """ View for displaying a single order's details """
    order = get_object_or_404(Order.objects.select_related('product'), id=order_id, user=request.user)
    return render(request, 'trading/order_detail.html', {'order': order})


@login_required
def transaction_list(request):
    """ View for displaying all transactions of the current user """
    transactions = Transaction.objects.filter(order__user=request.user).select_related('order')
    return render(request, 'trading/transaction_list.html', {'transactions': transactions})


@login_required
def create_order(request, product_id):
    """ View for creating an order for a product"""
    product = get_object_or_404(Product, id=product_id)

    if product.user == request.user:
        return redirect('product_detail', product_id=product.id)  # Redirect back to product

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.product = product
            order.total_price = product.price * order.quantity
            order.save()
            return redirect('payment_page', order_id=order.id)  # Updated redirection
    else:
        form = OrderForm(initial={'quantity': 1})

    return render(request, 'trading/create_order.html', {'form': form, 'product': product})


@login_required
def payment_page(request, order_id):
    """ View to redirect users to Stripe Checkout """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'kzt',
                'product_data': {
                    'name': order.product.title,
                },
                'unit_amount': int(order.total_price * 100),
            },
            'quantity': order.quantity,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(f"/orders/{order.id}/success/"),
        cancel_url=request.build_absolute_uri(f"/orders/{order.id}/payment/"),
    )

    return redirect(session.url)


@login_required
def payment_success(request, order_id):
    """ Verifies payment with Stripe before marking order as paid """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Ensure the order has a Stripe Payment Intent
    if not order.stripe_payment_intent:
        return redirect('order_detail', order_id=order.id)  # Prevents fake success calls

    try:
        # Retrieve the payment intent from Stripe
        intent = stripe.PaymentIntent.retrieve(order.stripe_payment_intent)

        # Verify payment status
        if intent.status == "succeeded":
            order.status = "paid"
            order.save()

            # Create a transaction record
            Transaction.objects.create(
                order=order,
                payment_intent_id=intent.id,
                payment_status="paid"
            )

            return render(request, "trading/payment_success.html", {"order": order})

    except stripe.error.StripeError:
        # Stripe API failed
        return redirect('order_detail', order_id=order.id)

    # If payment was not successful, redirect back to order page
    return redirect('order_detail', order_id=order.id)


@login_required
def cancel_order(request, order_id):
    """ Allows only the order owner to cancel their pending order """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != 'pending':
        return redirect('order_detail', order_id=order.id)  # Prevents canceling after payment

    order.status = 'cancelled'
    order.save()
    return redirect('order_detail', order_id=order.id)