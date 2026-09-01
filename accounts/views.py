from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .forms import LoginForm, RegisterForm


def login_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    if request.method == 'POST':

        form = LoginForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(
                username=username,
                password=password
            )

            if user is not None:

                login(request, user)

                messages.success(
                    request,
                    'Login successful!'
                )

                return redirect(
                    'dashboard:dashboard'
                )

    else:
        form = LoginForm()

    return render(
        request,
        'accounts/login.html',
        {
            'form': form
        }
    )


def register_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save(
                commit=False
            )

            user.set_password(
                form.cleaned_data['password']
            )

            user.save()

            messages.success(
                request,
                'Account created successfully!'
            )

            return redirect(
                'accounts:login'
            )

    else:
        form = RegisterForm()

    return render(
        request,
        'accounts/register.html',
        {
            'form': form
        }
    )


def profile(request):

    if not request.user.is_authenticated:
        return redirect('accounts:login')

    return render(
        request,
        'accounts/profile.html'
    )


def logout_view(request):

    logout(request)

    messages.success(
        request,
        'You have been logged out.'
    )

    return redirect(
        'accounts:login'
    )