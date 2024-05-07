from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('index', views.index, name='index'),
    path('login', views.login, name="login"),
    path('logOut', views.logOut, name="logOut"),
    path('info', views.info, name="info"),
]
