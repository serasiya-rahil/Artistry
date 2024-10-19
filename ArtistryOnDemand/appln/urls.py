from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('login_user/', views.login_user, name="login_user"),
    path('UserSignup/', views.UserSignup, name= "UserSignup"),
    path('ArtistSignup/', views.artist_signup, name='artist_signup'),
    path('loginArtist/', views.artist_login, name='artist_login'),
    path('artistDashboard/', views.artistDashboard, name='artistDashboard'),
    path('artistDashboard/add-artwork/', views.add_artwork, name='add_artwork'),
    path('artistDashboard/delete-artwork/<int:artwork_id>/', views.delete_artwork, name='delete_artwork'),
    path('edit_artwork/<int:artwork_id>/', views.edit_artwork, name='edit_artwork'),
    path('UserView/', views.UserView, name='UserView'),
    path('view_profile/', views.view_profile, name='view_profile'),
    path('edit_profile/<int:artist_id>', views.edit_profile, name='edit_profile'),
    path('logout/', views.custom_logout, name='logout'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

