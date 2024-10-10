from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login_user/', views.login_user, name="login_user"),
    path('UserSignup/', views.UserSignup, name= "UserSignup"),
    path('ArtistSignup/', views.artist_signup, name='artist_signup'),
    path('loginArtist/', views.artist_login, name='artist_login'),
    path('artistDashboard/', views.artistDashboard, name='artistDashboard'),
]
