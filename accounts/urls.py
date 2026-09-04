from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [

    # Login
    path(
        "login/",
        views.login_view,
        name="login"
    ),

    # Register
    path(
        "register/",
        views.register_view,
        name="register"
    ),

    # Logout
    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),
]