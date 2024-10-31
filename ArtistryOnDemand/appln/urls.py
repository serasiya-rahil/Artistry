from . import views
from django.urls import path
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
    path('View-Artwork-By-Id/<int:artwork_id>', views.viewArtworkById, name='viewArtworkById'),
    path('Order-Now/<int:artwork_id>', views.orderNow, name='orderNow'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('View-Past-Orders/', views.PastOrders, name='PastOrders'),
    path('Edit-Request/<int:request_id>', views.edit_request, name='edit_request'),
    path('View-Request-For-Artist/', views.ViewRequestForArtist, name='ViewRequestForArtist'),
    path('update-request-status/', views.update_request_status, name='update_request_status'),
    path('request/<int:request_id>/', views.view_request, name='view_request'),
    path('logout/', views.custom_logout, name='logout'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

