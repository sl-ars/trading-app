from django import forms
from trading.models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1})
        }