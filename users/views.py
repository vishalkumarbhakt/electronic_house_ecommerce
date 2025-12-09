from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages


def user_login(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})


def user_register(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


def user_logout(request):
    """User logout view."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required
def user_profile(request):
    """User profile view."""
    return render(request, 'users/profile.html')


@login_required
def user_dashboard(request):
    """User dashboard with order history."""
    # Get user's orders (Order model has user FK with related_name='orders')
    orders = request.user.orders.all().order_by('-created_at')[:5]
    # Get user's wishlist (Wishlist model has user FK with related_name='wishlist_items')
    wishlist = request.user.wishlist_items.all().order_by('-created_at')[:5]
    
    return render(request, 'users/dashboard.html', {
        'orders': orders,
        'wishlist': wishlist,
    })
