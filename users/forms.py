from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from users.models import User


class RegisterForm(UserCreationForm):
    """ Registration Form with Django validation, including phone number and avatar """

    role = forms.ChoiceField(choices=[
        ('customer', 'Customer'),
        ('trader', 'Trader'),
        ('sales_rep', 'Sales Representative')
    ], widget=forms.Select(attrs={'class': 'form-control'}))

    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'})
    )

    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'avatar', 'password1', 'password2', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
        }


class LoginForm(AuthenticationForm):
    """ Custom Login Form with Bootstrap styling """
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}))