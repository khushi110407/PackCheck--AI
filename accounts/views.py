from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        # Check empty fields
        if not username or not password:

            messages.error(
                request,
                "Please enter username and password."
            )

            return render(
                request,
                "accounts/login.html"
            )

        # Authenticate user
        user = authenticate(
            request,
            username=username,
            password=password
        )

        # Login successful
        if user is not None:

            login(
                request,
                user
            )

            messages.success(
                request,
                f"Welcome back, {user.username}!"
            )

            return redirect(
                "dashboard:dashboard"
            )

        # Login failed
        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "accounts/login.html"
    )


# =========================================================
# REGISTER
# =========================================================

def register_view(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        # ---------------------------------------------
        # Username validation
        # ---------------------------------------------

        if not username:

            messages.error(
                request,
                "Username is required."
            )

            return render(
                request,
                "accounts/register.html"
            )

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return render(
                request,
                "accounts/register.html"
            )

        # ---------------------------------------------
        # Email validation
        # ---------------------------------------------

        if not email:

            messages.error(
                request,
                "Email address is required."
            )

            return render(
                request,
                "accounts/register.html"
            )

        if User.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                "Email is already registered."
            )

            return render(
                request,
                "accounts/register.html"
            )

        # ---------------------------------------------
        # Password validation
        # ---------------------------------------------

        if not password:

            messages.error(
                request,
                "Password is required."
            )

            return render(
                request,
                "accounts/register.html"
            )

        if len(password) < 8:

            messages.error(
                request,
                "Password must contain at least 8 characters."
            )

            return render(
                request,
                "accounts/register.html"
            )

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                "accounts/register.html"
            )

        # ---------------------------------------------
        # Create user
        # ---------------------------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(
            request,
            "Account created successfully. Please login."
        )

        return redirect(
            "accounts:login"
        )

    return render(
        request,
        "accounts/register.html"
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect(
        "accounts:login"
    )