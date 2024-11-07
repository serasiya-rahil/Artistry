import os
import json
import re
import shutil
import stripe
from .Debug import *
from django.db import models
from datetime import datetime
from django.db.models import Avg
from .logout_middleware import *
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponse
from .models import User as CustomUser
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from .models import Artist, Artwork, ArtistProfile, User as userModel, Feedback, Request, Order, Upload
from .forms import CustomUserSignupForm, ArtistSignupForm, ArtistLoginForm, ArtworkForm, EditArtworkForm, ArtistProfileForm, RequestForm, UploadForm


dbg = SimpleDebugger(enabled=True)
lgt = SessionExpiryMiddleware(MiddlewareMixin)

#STRIPE API KEY FROM SETTINGS
stripe.api_key = settings.STRIPE_SECRET_KEY 

def home(request):
    
    lgt.process_request(request)
    if(request.user):
        dbg.info(f"User {request.user} logged in")
    else:
        dbg.info(f"No User is Logged In Currently")

    artworks = Artwork.objects.all()
    Profile_artworks = None
    
    dbg.info(f"Rendering Page home.html...")
    return render(request, 'appln/home.html', {'artworks': artworks,'Profile_artworks':Profile_artworks})

def UserSignup(request):
    if request.method == 'POST':
        form = CustomUserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user:
                dbg.info(f"User Saved in Db User:{request.user}")
            else:
                dbg.error("Failed to saved the user")
            login(request, user)  
            return redirect('home')
        else:
            dbg.error(f"Signup form is not valid...Proceed to send signup form")
    else:
        dbg.info(f"User requested for a signup form")
        form = CustomUserSignupForm()
    
    dbg.info(f"Rendering UserSignup.html for Signup...")
    return render(request, 'appln/UserSignup.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        dbg.info(f"Attempting to log in user: {username}")
        
        try:
            userObj = userModel.objects.get(username=username)
            dbg.info(f"User found: {userObj.username}")
        except:
            messages.error(request, "User does not exist.")
            dbg.error(f"User does not exist: {username}")
            
            return render(request, 'appln/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            dbg.info(f"User logged in {request.user}")
            return redirect('UserView')  
        else:
            dbg.error(f"Login failed for user: {username}")
            messages.error(request, 'Invalid username or password.')
            return render(request, 'appln/login.html') 
    else:
        dbg.info("Displaying login page.")
        return render(request, 'appln/login.html')
    
def artist_signup(request):
    if request.method == 'POST':
        form = ArtistSignupForm(request.POST)
        dbg.info("Processing artist signup form.")
        if form.is_valid():
            artist = form.save()
            dbg.info(f"Artist signed up successfully: {artist.username}")
            user = User.objects.get(username=artist.username)
            login(request, user)
            dbg.info(f"User logged in: {user}")
            return redirect('home')  
        else:
            dbg.error("Artist signup form is not valid.")
    else:
        dbg.info("Displaying artist signup form.")
        form = ArtistSignupForm()

    return render(request, 'appln/artist_signup.html', {'form': form})

def artist_login(request):
    if request.method == 'POST':
        form = ArtistLoginForm(request.POST)
        dbg.info("Processing artist login form.")
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            try:
                artist = Artist.objects.get(username=username)
                dbg.info(f"Artist found: {artist.username}")
            except Artist.DoesNotExist:
                messages.error(request, "Artist does not exist.")
                dbg.error(f"Artist does not exist: {username}")
                return render(request, 'appln/artist_login.html', {'form': form})
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                
                login(request, user) 
                dbg.info(f"User logged in: {user}")
                return redirect("artistDashboard")
            else:
                messages.error(request, "Invalid credentials. Please try again.")
                dbg.error("Invalid credentials for artist login.")
    else:
        dbg.info("Displaying artist login form.")
        form = ArtistLoginForm()

    return render(request, 'appln/artist_login.html', {'form': form})

@login_required
def artistDashboard(request):
    try:
        dbg.info(f"Current User: {request.user}")
        artist = Artist.objects.get(username=request.user)
        dbg.info(f"Artist found: {artist.username}")
        
        artworks = Artwork.objects.filter(artist=artist)
        dbg.info(f"Total artworks found: {artworks.count()}")
        
        profile = ArtistProfile.objects.filter(artist_id=artist.artist_id).first()
        if not profile:
            messages.warning(request, "Your Profile is missing few details, Kindly update your profile")
            dbg.warn(f"Please Update your profile: {request.user}")
            
        total_artworks = artworks.count()
        
        search_query = request.GET.get('search', '')
        if search_query:
            artworks = artworks.filter(title__icontains=search_query)
            dbg.info(f"Search query applied: {search_query}, Total artworks after search: {artworks.count()}")
            
    except Artist.DoesNotExist:
        artworks = []
        artist = None 
        profile=None
        dbg.error(f"Artist does not exist for user: {request.user}")

    return render(request, 'appln/artistDashboard.html', {'artist': artist, 'artworks': artworks, 'total_artworks': total_artworks, 'search_query': search_query,'profile': profile
    })

@login_required
def add_artwork(request):
    artistobj = Artist.objects.get(username=request.user)
    dbg.info(f"Adding artwork for artist: {artistobj.username}")
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES) 
        if form.is_valid():
            artwork = form.save(commit=False)  
            
            artwork.artist=artistobj
            dbg.info(f"Saving artwork: {artwork.title} for artist: {artistobj.username}")
            
        
            artwork.save() 
            dbg.info(f"Artwork saved successfully: {artwork.title}")
            return redirect('artistDashboard')  
    else:
        form = ArtworkForm()
        try:
            profile = get_object_or_404(ArtistProfile,artist_id=artistobj.artist_id)
            dbg.info(f"Profile found for artist: {artistobj.username}")
        except:
            profile = None
            dbg.error(f"Profile not found for artist: {artistobj.username}")

            
    return render(request, 'appln/add_artwork.html', {'form': form})

@login_required
def delete_artwork(request, artwork_id):
    artist = get_object_or_404(Artist, username=request.user)
    artwork = get_object_or_404(Artwork, artwork_id=artwork_id, artist=artist)
    dbg.info(f"Attempting to delete artwork: {artwork.title} by artist: {artist.username}")
    
    if request.method == "POST":
        if artwork.image_path and os.path.isfile(artwork.image_path.path):
            os.remove(artwork.image_path.path)
            dbg.info(f"Deleted image at path: {artwork.image_path.path}")

        if artwork.video_path and os.path.isfile(artwork.video_path.path):
            os.remove(artwork.video_path.path)
            dbg.info(f"Deleted video at path: {artwork.video_path.path}")
            
        artwork.delete()
        dbg.info(f"Artwork deleted successfully: {artwork.title}")
        return redirect('artistDashboard')  
    
    dbg.warn(f"Delete request was not a POST request for artwork: {artwork.title}")
    return redirect('artistDashboard') 

@login_required
def edit_artwork(request, artwork_id):
    artwork = get_object_or_404(Artwork, artwork_id=artwork_id, artist__username=request.user)
    dbg.info(f"Editing artwork: {artwork.title} (ID: {artwork_id}) by artist: {request.user.username}")

    old_image_path = artwork.image_path.path if artwork.image_path else None
    old_video_path = artwork.video_path.path if artwork.video_path else None

    if request.method == 'POST':
        form = EditArtworkForm(request.POST, request.FILES, instance=artwork)
        if form.is_valid():
            if 'image_path' in request.FILES and old_image_path:
                if os.path.isfile(old_image_path):
                    os.remove(old_image_path)  
                    dbg.info(f"Old image deleted: {old_image_path}")
           
            if 'video_path' in request.FILES and old_video_path:
                if os.path.isfile(old_video_path):
                    os.remove(old_video_path) 
                    dbg.info(f"Old video deleted: {old_video_path}")

            artwork = form.save(commit=False)  
            # Save new paths for image and video
            if 'image_path' in request.FILES:
                artwork.image_path = request.FILES['image_path']
                dbg.info(f"New image uploaded: {artwork.image_path.name}")

            if 'video_path' in request.FILES:
                artwork.video_path = request.FILES['video_path']
                dbg.info(f"New video uploaded: {artwork.video_path.name}")

            artwork.save()
            dbg.info(f"Artwork updated successfully: {artwork.title}")
            return redirect('artistDashboard')
    else:
        form = EditArtworkForm(instance=artwork)

    dbg.info("Rendering edit artwork form.")
    return render(request, 'appln/edit_artwork.html', {
        'form': form,
        'artwork': artwork,
    })

@login_required
def UserView(request):
    dbg.info("Fetching all artworks for UserView.")
    artworks = Artwork.objects.all()
    Profile_artworks = Artwork.objects.select_related('artist').prefetch_related('artist__profiles').all()
    order_count = Order.objects.filter(user_id=request.user.id).count()

    search_query = request.GET.get('search', '')
    if search_query:
        dbg.info(f"Search query received: {search_query}")
        artworks = artworks.filter(title__icontains=search_query)
        dbg.info(f"Filtered artworks based on search query: {search_query} (Total: {artworks.count()})")
    else:
        dbg.info(f"No search query provided. Total artworks: {artworks.count()}")

    for artwork in artworks:
        # Use the correct filtering for feedbacks via request
        rating = Feedback.objects.filter(request__artwork=artwork).aggregate(Avg('rating'))['rating__avg']
        artwork.average_rating = rating if rating is not None else "No ratings yet"

    dbg.info("Rendering UserHomePage.")
    return render(request, 'appln/UserHomePage.html', {
        'artworks': artworks,
        'search_query': search_query,
        'Profile_artworks': Profile_artworks,
        'order_count':order_count
    })

@login_required
def custom_logout(request):
    dbg.info(f"User {request.user} is logging out.")
    logout(request)
    dbg.info("User successfully logged out. Flushing session data.")
    request.session.flush()
    dbg.info("Session data flushed.")
    return redirect('home')

@login_required
def view_profile(request):
    dbg.info(f"Attempting to view profile for user: {request.user}")
    
    artist = get_object_or_404(Artist, username=request.user)
    dbg.info(f"Artist found: {artist.username}")
    
    profile = ArtistProfile.objects.filter(artist_id=artist.artist_id).first()
    if not profile:
        dbg.warn(f"No Profile retrieved for artist ID {artist.artist_id}")
       
    try:
        artist_profile = ArtistProfile.objects.get(artist=artist)
        dbg.info(f"Artist profile found: {artist_profile}")
    except ArtistProfile.DoesNotExist:
        artist_profile = None
        dbg.warn(f"No profile found for artist: {artist.username}")

    return render(request, 'appln/artist_profile_form.html', {'artist_profile': artist_profile,'profile':profile})

def edit_profile(request, artist_id):
    artist_profile = get_object_or_404(ArtistProfile, artist_id=artist_id)
    
    if request.method == 'POST':
        form = ArtistProfileForm(request.POST, request.FILES, instance=artist_profile)
        
        if form.is_valid():
            
            social_links = form.cleaned_data.get('social_links', '')
            if social_links:
               
                links_list = [link.strip() for link in social_links.split(',')]
                form.instance.social_links = ', '.join(links_list) 
            
            if 'profile_photo' in request.FILES:
               
                if artist_profile.profile_photo:
                    old_photo_path = artist_profile.profile_photo.path
                    print(f"Attempting to delete: {old_photo_path}")  
                    if os.path.isfile(old_photo_path):
                        try:
                            os.remove(old_photo_path)
                            print(f"Deleted: {old_photo_path}")  
                        except Exception as e:
                            print(f"Error deleting file: {e}")  
            
            form.save()
            return redirect('view_profile') 
    else:
        artist_profile=None
        form = ArtistProfileForm(instance=artist_profile)

    return render(request, 'appln/edit_profile.html', {'form': form, 'artist_profile': artist_profile})

def viewArtworkById(request, artwork_id):
    artwork = None
    try:
        artwork = Artwork.objects.get(artwork_id=artwork_id)
        dbg.info(f"Artwork Found with ID: '{artwork_id}'")
        
        rating = Feedback.objects.filter(request__artwork=artwork).aggregate(Avg('rating'))['rating__avg']
        artwork.average_rating = rating if rating is not None else 0
       
        return render(request, 'appln/ArtworkById.html', { 'artwork': artwork })

    except Artwork.DoesNotExist:
        dbg.error(f"No Artwork Found with ID: '{artwork_id}'")
        messages.error(request, "No Artwork Found")
        
    except Exception as e:
        dbg.error(f"Error retrieving artwork with ID: '{artwork_id}': {str(e)}")
        messages.error(request, "Something Went Wrong")

    return render(request, 'appln/ArtworkById.html', {'artwork': artwork})

def orderNow(request, artwork_id):
    artwork = get_object_or_404(Artwork, pk=artwork_id)
    
    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Create Stripe session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'cad',
                        'product_data': {
                            'name': artwork.title,
                        },
                        'unit_amount': int(artwork.price * 100),  
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/success/') + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=request.build_absolute_uri('/cancel/'),
            )

            # Initialize temp_form_data for session storage
            temp_form_data = {
                'description': form.cleaned_data['description'],
                'artwork_id': artwork_id,
                'user_id': request.user.id,
            }
            
            # Use FileSystemStorage to save files temporarily in media/tmp/
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'tmp'))
            
            if 'image_path' in request.FILES:
                image_file = request.FILES['image_path']
                image_filename = fs.save(image_file.name, image_file)
                temp_form_data['image_path'] = image_filename  # Save the filename, not the URL

            if 'video_path' in request.FILES:
                video_file = request.FILES['video_path']
                video_filename = fs.save(video_file.name, video_file)
                temp_form_data['video_path'] = video_filename  # Save the filename, not the URL

            # Save the temporary form data in session
            request.session['temp_form_data'] = temp_form_data

            return JsonResponse({'sessionId': session.id})

    else:
        form = RequestForm()

    return render(request, 'appln/order_now.html', {'form': form, 'artwork': artwork, 'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY})

def payment_success(request):
    session_id = request.GET.get('session_id')
    
    if session_id:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            temp_data = request.session.pop('temp_form_data', None)
            

            if temp_data:
                # Create a new request record
                request_instance = Request.objects.create(
                    description=temp_data['description'],
                    user_id=temp_data['user_id'],
                    artwork_id=temp_data['artwork_id'],
                    artist_id=Artwork.objects.get(pk=temp_data['artwork_id']).artist_id,
                    status='pending',
                    created_at=datetime.now()
                )
                RequestNumber = request_instance.request_id
                

                # Move image from media/tmp/ to media/images/artworks/
                if temp_data.get('image_path'):
                    image_temp_path = os.path.join('tmp', temp_data['image_path'])
                    image_permanent_path = f"images/artworks/{RequestNumber}/image_{RequestNumber}.jpg"
                    if move_file_to_permanent_storage(image_temp_path, image_permanent_path):
                        request_instance.image_path = image_permanent_path

                # Move video from media/tmp/ to media/videos/artworks/
                if temp_data.get('video_path'):
                    video_temp_path = os.path.join('tmp', temp_data['video_path'])
                    video_permanent_path = f"videos/artworks/{RequestNumber}/video_{RequestNumber}.mp4"
                    if move_file_to_permanent_storage(video_temp_path, video_permanent_path):
                        request_instance.video_path = video_permanent_path

                request_instance.save()

                # Create the order record
                order_instance = Order(
                    total_price=Artwork.objects.get(pk=temp_data['artwork_id']).price,
                    order_status='pending',
                    created_at=datetime.now(),
                    artist_id=Artwork.objects.get(pk=temp_data['artwork_id']).artist_id,
                    artwork=Artwork.objects.get(pk=temp_data['artwork_id']),
                    user=CustomUser.objects.get(username=request.user.username)
                )
                order_instance.request = request_instance
                order_instance.save()

                messages.success(request, f"Order Placed Successfully with Order ID: {order_instance.order_id}")
                return redirect('UserView')

    return redirect('orderNow')

def move_file_to_permanent_storage(temp_path, permanent_path):
    temp_full_path = os.path.join(settings.MEDIA_ROOT, temp_path)
    permanent_full_path = os.path.join(settings.MEDIA_ROOT, permanent_path)
    
    os.makedirs(os.path.dirname(permanent_full_path), exist_ok=True)

    if os.path.exists(temp_full_path):
        try:
            shutil.move(temp_full_path, permanent_full_path)
            return True
        except Exception as e:
            return False
    else:
        return False

def payment_cancel(request):
    return render(request, 'payment_cancel.html')

def PastOrders(request):
    try:
        allOrders = Order.objects.filter(user_id=request.user.id)
        dbg.info(f"Orders Count: {allOrders.count()}")

        for order in allOrders:
            dbg.info(f"Order found: {order.order_id}")
            dbg.info(f"Artwork ID: {order.artwork.artwork_id}")
            dbg.info(f"Status: {order.request.status}")

    except:
        allOrders = None

    return render(request, 'appln/PastOrders.html',{'allOrders':allOrders})

def edit_request(request, request_id):
    request_instance = get_object_or_404(Request, request_id=request_id)
    RequestNumber = request_instance.request_id

    # Check if the request is editable
    if not request_instance.is_editable():
        messages.info(request,"This request cannot be edited as it has already passed the allowed time for modifications.")
        return redirect('PastOrders')

    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES, instance=request_instance)

        if form.is_valid():
            # Track changes in the instance
            changes_made = False

            # Check for image upload
            if 'image_path' in request.FILES and request.FILES['image_path']:
                image_file = request.FILES['image_path']

                # If a new image is uploaded, delete the old one and update the path
                if request_instance.image_path:
                    old_image_path = os.path.join(settings.MEDIA_ROOT, request_instance.image_path)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)  # Delete the old image if it exists

                # Update the image path
                request_instance.image_path = f"images/artworks/{RequestNumber}/image_{RequestNumber}.jpg"
                changes_made = True

                # Ensure the target directory exists
                target_directory = os.path.dirname(os.path.join(settings.MEDIA_ROOT, request_instance.image_path))
                if not os.path.exists(target_directory):
                    os.makedirs(target_directory)

                # Save the new image directly to the permanent path
                with open(os.path.join(settings.MEDIA_ROOT, request_instance.image_path), 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)

            # Check for video upload
            if 'video_path' in request.FILES and request.FILES['video_path']:
                video_file = request.FILES['video_path']

                # If a new video is uploaded, delete the old one and update the path
                if request_instance.video_path:
                    old_video_path = os.path.join(settings.MEDIA_ROOT, request_instance.video_path)
                    if os.path.exists(old_video_path):
                        os.remove(old_video_path)  # Delete the old video if it exists

                # Update the video path
                request_instance.video_path = f"videos/artworks/{RequestNumber}/video_{RequestNumber}.mp4"
                changes_made = True

                # Ensure the target directory exists
                target_directory = os.path.dirname(os.path.join(settings.MEDIA_ROOT, request_instance.video_path))
                if not os.path.exists(target_directory):
                    os.makedirs(target_directory)

                # Save the new video directly to the permanent path
                with open(os.path.join(settings.MEDIA_ROOT, request_instance.video_path), 'wb+') as destination:
                    for chunk in video_file.chunks():
                        destination.write(chunk)

            # If any changes were made (to image or video), save the instance
            if changes_made:
                request_instance.save()  # Save the instance after changes

            messages.success(request, "Request updated successfully.")
            return redirect('UserView')  # Adjust this as necessary

    else:
        form = RequestForm(instance=request_instance)

    return render(request, 'appln/edit_request.html', {'form': form, 'request': request_instance})

@login_required
def ViewRequestForArtist(request):
    artistToSearch = Artist.objects.get(username=request.user)
    
    try:
        allRequests = Request.objects.filter(artist_id=artistToSearch.artist_id)
        for req in allRequests:
            dbg.info(f"Request id: {req.request_id}")
    except Request.DoesNotExist:
        allRequests = None

    status_choices = Request._meta.get_field('status').choices
    
    return render(request, 'appln/View_requests_for_artist.html', {
        'allRequests': allRequests,
        'status_choices': status_choices,
    })

def update_request_status(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        new_status = request.POST.get('status')
        
        req_instance = get_object_or_404(Request, pk=request_id)

        req_instance.status = new_status
        req_instance.save()

        return JsonResponse({'success': True, 'new_status': new_status})
    
    return JsonResponse({'success': False})

#Artist will view this when a request is made by the user
@login_required
def view_request(request, request_id):
    artistProfile = Artist.objects.get(username=request.user)

    request_instance = get_object_or_404(Request, request_id=request_id)

    if request.method == 'POST':
        # Update the request details
        request_instance.deadline = request.POST.get('deadline')
        request_instance.artist_accept_date = request.POST.get('artist_accept_date')
        request_instance.artist_delivery_date = request.POST.get('artist_delivery_date')
        request_instance.save()
        return redirect('view_request', request_id=request_instance.request_id)

    context = {
        'request': request_instance
    }
    
    return render(request, 'appln/view_requestByID.html', context)

def upload_file(request, request_id):
    # Get the Request instance by request_id
    request_instance = Request.objects.get(request_id=request_id)

    # Check if an upload already exists for this request
    upload_instance = Upload.objects.filter(request=request_instance).first()

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES, instance=upload_instance)  # If upload_instance exists, pre-populate the form with it
        if form.is_valid():
            # Save the form data to the upload_instance (this could be new or an update)
            upload_instance = form.save(commit=False)
            upload_instance.request = request_instance  # Ensure request is set correctly
            
            # Optionally, set the artist if it's not handled in the form
            upload_instance.artist = request_instance.artist  # Assuming the request has an artist linked

            # Save the upload instance
            upload_instance.save()

            # After saving the upload, mark the request as fulfilled and set the artist_delivery_date
            request_instance.status = 'fulfilled'
            request_instance.artist_delivery_date = timezone.now()  # Set to current time
            request_instance.save()

            # Update the associated Order status to completed and set the actual_delivery_date
            order_instance = Order.objects.get(request=request_instance)  # Assuming each request has an associated order
            order_instance.order_status = 'completed'
            order_instance.actual_delivery_date = timezone.now()  # Set to current time
            order_instance.save()

            # Redirect to a success page or back to the request view
            return redirect('ViewRequestForArtist')  # Replace with your actual URL name
    else:
        form = UploadForm(instance=upload_instance)  # If editing, pre-populate form with existing data

    return render(request, 'appln/upload_file.html', {'form': form, 'request': request_instance})

def upload_details(request, request_id):
  
    request_instance = get_object_or_404(Request, request_id=request_id)
    
    try:
        upload_instance = Upload.objects.get(request=request_instance)
    except Upload.DoesNotExist:
        upload_instance = None
    
    return render(request, 'appln/upload_details.html', {
        'request': request_instance,
        'upload': upload_instance
    })

from django.shortcuts import render, get_object_or_404, redirect
from .models import Request, Feedback
from .forms import FeedbackForm

def give_feedback(request, request_id):
    request_instance = get_object_or_404(Request, request_id=request_id)
    currenrUser = userModel.objects.get(username=request.user)
    existing_feedback = Feedback.objects.filter(request=request_instance).first()
    star_values = [5, 4, 3, 2, 1]

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            if existing_feedback:
                feedback = existing_feedback
                feedback.rating = form.cleaned_data['rating']
                feedback.comments = form.cleaned_data['comments']
                messages.success(request,"Rating Edited Successfully")
            else:
                feedback = form.save(commit=False)
                feedback.request = request_instance
                feedback.user = currenrUser
                messages.success(request,"Rating Provided Successfully")
            feedback.save()
           
            return redirect('UserView')
    else:
        if existing_feedback:
            form = FeedbackForm(instance=existing_feedback)
            existing_rating = existing_feedback.rating  # Ensure it's an integer
        else:
            form = FeedbackForm()
            existing_rating = None

    return render(request, 'appln/feedback_form.html', {
        'form': form,
        'request': request_instance,
        'existing_rating': existing_rating,  # This will be an integer,
        'star_values': star_values,
    })

 

