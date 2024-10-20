import os
import json
from .Debug import *
from .logout_middleware import *
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Artist, Artwork, ArtistProfile, User as userModel
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserSignupForm, ArtistSignupForm, ArtistLoginForm, ArtworkForm, EditArtworkForm, ArtistProfileForm

#set debugging to True or False
dbg = SimpleDebugger(enabled=True)
#create Session expiry object
lgt = SessionExpiryMiddleware(MiddlewareMixin)

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

    search_query = request.GET.get('search', '')
    if search_query:
        dbg.info(f"Search query received: {search_query}")
    
    if search_query:
        artworks = artworks.filter(title__icontains=search_query)
        dbg.info(f"Filtered artworks based on search query: {search_query} (Total: {artworks.count()})")
    else:
        dbg.info(f"No search query provided. Total artworks: {artworks.count()}")
        
    dbg.info("Rendering UserHomePage.")
    return render(request, 'appln/UserHomePage.html', {'artworks': artworks, 'search_query':search_query,'Profile_artworks':Profile_artworks})

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

    #messages.success(request, 'Your profile has been updated successfully!')
    #messages.error(request, 'An error occurred while updating your profile.')
    #messages.warning(request, 'Please check the information you provided.')
    #messages.info(request, 'Your changes have been saved.')

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
        form = ArtistProfileForm(instance=artist_profile)

    return render(request, 'appln/edit_profile.html', {'form': form, 'artist_profile': artist_profile})
