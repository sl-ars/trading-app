from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import User
from users.forms import RegisterForm, LoginForm

def register_view(request):
    """ Handles user registration via Django templates """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    """ Handles user login via Django templates """
    next_url = request.GET.get('next', 'profile')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})

@login_required
def profile_view(request):
    """ Displays the user profile via Django templates """
    return render(request, 'users/profile.html')

@login_required
def logout_view(request):
    """ Handles user logout via Django templates """
    if request.method == "POST":
        logout(request)
        messages.info(request, "You have successfully logged out.")
    return redirect('login')



