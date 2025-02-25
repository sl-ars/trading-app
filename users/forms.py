from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from users.models import User

class RegisterForm(UserCreationForm):
    """ Registration Form with Django validation """
    role = forms.ChoiceField(choices=[
        ('customer', 'Customer'),
        ('trader', 'Trader'),
        ('sales', 'Sales Representative')
    ])

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

class LoginForm(AuthenticationForm):
    """ Custom Login Form with Bootstrap styling """
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Enter username'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Enter password'})