from django import forms
from trading.models import Order
from .models import Product

class ProductListingForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'category', 'image']

    def __init__(self, *args, **kwargs):
        super(ProductListingForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'rows': 3})
        self.fields['price'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Price in ₸'})
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})