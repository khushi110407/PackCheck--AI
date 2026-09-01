from django.urls import path

from . import views


app_name = 'compliance'


urlpatterns = [

    path(
        'violations/',
        views.violations,
        name='violations'
    ),

    path(
        'details/<int:pk>/',
        views.details,
        name='details'
    ),

]