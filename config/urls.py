from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static


def home(request):
    return redirect('dashboard:dashboard')


urlpatterns = [

    path(
        '',
        home,
        name='home'
    ),

    path(
        'admin/',
        admin.site.urls
    ),

    path(
        'accounts/',
        include('accounts.urls')
    ),

    path(
        'scanner/',
        include('scanner.urls')
    ),

    path(
        'compliance/',
        include('compliance.urls')
    ),

    path(
        'reports/',
        include('reports.urls')
    ),

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