from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django_filters.rest_framework import DjangoFilterBackend
from .forms import ProductListingForm
from .models import Product, Category
from trading_app.permissions import IsAdmin, IsManager, IsSeller, IsOwnerOrAdmin, IsAdminOrReadOnly





### ==== Django Template Views (Frontend) ==== ###


def product_list(request):
    """ Renders the main page with all product listings """
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

@login_required
def product_create(request):
    """ Handles product listing creation via Django templates """
    if request.method == "POST":
        form = ProductListingForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            return redirect('product_list')
    else:
        form = ProductListingForm()
    return render(request, 'products/product_create.html', {'form': form})

def product_detail(request, product_id):
    """ Renders the product detail page """
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/product_detail.html', {'product': product})


@login_required
def product_edit(request, product_id):
    """ Handles editing an existing product """
    product = get_object_or_404(Product, id=product_id, user=request.user)
    if request.method == "POST":
        form = ProductListingForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductListingForm(instance=product)
    return render(request, 'products/product_edit.html', {'form': form, 'product': product})

@login_required
def product_delete(request, product_id):
    """ Handles deleting a product listing """
    product = get_object_or_404(Product, id=product_id, user=request.user)
    if request.method == "POST":
        product.delete()
        return redirect('product_list')
    return render(request, 'products/product_delete.html', {'product': product})


@login_required
def user_listings(request):
    """ Shows the listings created by the logged-in user """
    products = Product.objects.filter(user=request.user)
    return render(request, 'products/user_listings.html', {'products': products})



