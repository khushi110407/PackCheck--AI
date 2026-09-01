from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static


def home(request):
    return redirect('dashboard:dashboard')


urlpatterns = [

    # Home
    path('', home, name='home'),

    # Admin
    path('admin/', admin.site.urls),

    # Accounts
    path(
        'accounts/',
        include('accounts.urls')
    ),

    # Scanner
    path(
        'scanner/',
        include('scanner.urls')
    ),

    # Compliance
    path(
        'compliance/',
        include('compliance.urls')
    ),

    # Reports
    path(
        'reports/',
        include('reports.urls')
    ),

    # Dashboard
    path(
        'dashboard/',
        include('dashboard.urls')
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )