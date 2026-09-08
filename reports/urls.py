from django.urls import path

from . import views


app_name = 'reports'


urlpatterns = [

    path(
        'report/',
        views.report,
        name='report'
    ),

    path(
        'history/',
        views.history,
        name='history'
    ),

]