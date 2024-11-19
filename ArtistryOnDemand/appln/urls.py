from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('User-Login/', views.login_user, name="login_user"),
    path('User-Signup/', views.UserSignup, name= "UserSignup"),
    path('Artist-Signup/', views.artist_signup, name='artist_signup'),
    path('Artist-Login/', views.artist_login, name='artist_login'),
    path('Artist-Dashboard/', views.artistDashboard, name='artistDashboard'),
    path('Artist-Dashboard/Add-Artwork/', views.add_artwork, name='add_artwork'),
    path('Artist-Dashboar/Delete-Artwork/<int:artwork_id>/', views.delete_artwork, name='delete_artwork'),
    path('Edit-Artwork/<int:artwork_id>/', views.edit_artwork, name='edit_artwork'),
    path('View-User/', views.UserView, name='UserView'),
    path('View-Profile/', views.view_profile, name='view_profile'),
    path('Edit-Profile/<int:artist_id>', views.edit_profile, name='edit_profile'),
    path('View-Artwork-By-Id/<int:artwork_id>', views.viewArtworkById, name='viewArtworkById'),
    path('Order-Now/<int:artwork_id>', views.orderNow, name='orderNow'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('View-Past-Orders/', views.PastOrders, name='PastOrders'),
    path('Edit-Request/<int:request_id>', views.edit_request, name='edit_request'),
    path('View-Request-For-Artist/', views.ViewRequestForArtist, name='ViewRequestForArtist'),
    path('Update-Request-Status/', views.update_request_status, name='update_request_status'),
    path('Request/<int:request_id>/', views.view_request, name='view_request'),
    path('Upload/<int:request_id>/', views.upload_file, name='upload_file'),
    path('View-Artwork-For-Request/<int:request_id>/', views.upload_details, name='upload_details'),
    path('Feedback/<int:request_id>/', views.give_feedback, name='give_feedback'),
    path('Artist-Analytics/', views.dashboard, name='dashboard'),
    path('My-Listings/', views.myListings, name='myListings'),
    path('Services/', views.Services, name='Services'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('get-artwork-details/', views.get_artwork_details, name='get_artwork_details'),
    path('feedback/<int:artwork_id>/', views.artwork_feedback, name='artwork_feedback'),
    path('ContactUs/', views.ContactUs, name='ContactUs'),
    path('Artist-Feedback-View/', views.artist_feedback_view, name='artist_feedback_view'),
    path('logout/', views.custom_logout, name='logout'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



