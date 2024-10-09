from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login_user/', views.login_user, name="login_user"),
    path('signup/', views.signup, name= "signup"),
]
