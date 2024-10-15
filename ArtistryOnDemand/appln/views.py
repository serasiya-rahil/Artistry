import os
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Artist, Artwork, ArtistProfile
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserSignupForm, ArtistSignupForm, ArtistLoginForm, ArtworkForm, EditArtworkForm

def home(request):
    if(request.user):
        print(request.user)

    artworks = Artwork.objects.all()
    return render(request, 'appln/home.html', {'artworks': artworks})

def UserSignup(request):
    if request.method == 'POST':
        form = CustomUserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('home')
    else:
        form = CustomUserSignupForm()
    return render(request, 'appln/UserSignup.html', {'form': form})

#User Login View here
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
         
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            
            login(request, user)
            return redirect('UserView')  
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'appln/login.html') 
    else:
        return render(request, 'appln/login.html')
    
def artist_signup(request):
    if request.method == 'POST':
        form = ArtistSignupForm(request.POST)
        if form.is_valid():
            artist = form.save()
           
            user = User.objects.get(username=artist.username)
            
            login(request, user)
            return redirect('home')  
    else:
        form = ArtistSignupForm()

    return render(request, 'appln/artist_signup.html', {'form': form})

def artist_login(request):
    if request.method == 'POST':
        form = ArtistLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')


            # Check if the artist exists in the Artist table
            try:
                artist = Artist.objects.get(username=username)
            except Artist.DoesNotExist:
                messages.error(request, "Artist does not exist.")
                return render(request, 'appln/artist_login.html', {'form': form})

            # Authenticate the user using Django's built-in User model
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)  # Log the user in
                return redirect("artistDashboard")  # Redirect to the home page or artist dashboard
            else:
                messages.error(request, "Invalid credentials. Please try again.")
    else:
        form = ArtistLoginForm()

    return render(request, 'appln/artist_login.html', {'form': form})

@login_required
def artistDashboard(request):
    try:
        # Get the artist object for the current user
        artist = Artist.objects.get(username=request.user)
        # Fetch all artworks associated with this artist
        artworks = Artwork.objects.filter(artist=artist)
        total_artworks = artworks.count()
        
        #search query
        search_query = request.GET.get('search', '')
        if search_query:
            artworks = artworks.filter(title__icontains=search_query)
    except Artist.DoesNotExist:
        # Handle the case where the artist does not exist
        artworks = []
        artist = None  # or handle it according to your app logic

    return render(request, 'appln/artistDashboard.html', {
        'artist': artist,
        'artworks': artworks,
        'total_artworks': total_artworks,
        'search_query': search_query
    })

@login_required
def add_artwork(request):
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES) 
        if form.is_valid():
            artwork = form.save(commit=False)  
            artistob = Artist.objects.get(username=request.user)
            artwork.artist=artistob
            print(request.user)
        
            artwork.save() 
            return redirect('artistDashboard')  
    else:
        form = ArtworkForm()

    return render(request, 'appln/add_artwork.html', {'form': form})

@login_required
def delete_artwork(request, artwork_id):
   
    artist = get_object_or_404(Artist, username=request.user)
   
    artwork = get_object_or_404(Artwork, artwork_id=artwork_id, artist=artist)
    
    if request.method == "POST":
        if artwork.image_path and os.path.isfile(artwork.image_path.path):
            os.remove(artwork.image_path.path)

        if artwork.video_path and os.path.isfile(artwork.video_path.path):
            os.remove(artwork.video_path.path)
            
        artwork.delete()
        return redirect('artistDashboard')  
    
    return redirect('artistDashboard') 

@login_required
def edit_artwork(request, artwork_id):
    # Get the specific artwork by its ID
    artwork = get_object_or_404(Artwork, artwork_id=artwork_id, artist__username=request.user)

    old_image_path = artwork.image_path.path if artwork.image_path else None
    old_video_path = artwork.video_path.path if artwork.video_path else None

    if request.method == 'POST':
        # Bind the form to the POST data and files (for image/video uploads)
        form = EditArtworkForm(request.POST, request.FILES, instance=artwork)
        if form.is_valid():
            # Delete the old image if a new one is uploaded
            
            if 'image_path' in request.FILES and old_image_path:
                if os.path.isfile(old_image_path):
                    os.remove(old_image_path)  # Remove the old image file

            # Delete the old video if a new one is uploaded
            if 'video_path' in request.FILES and old_video_path:
                if os.path.isfile(old_video_path):
                    os.remove(old_video_path)  # Remove the old video file

            form.save()  # Save the changes to the artwork
            return redirect('artistDashboard')  # Redirect to dashboard after successful edit
    else:
        # For GET requests, populate the form with the artwork's existing data
        form = EditArtworkForm(instance=artwork)

    return render(request, 'appln/edit_artwork.html', {
        'form': form,
        'artwork': artwork,
    })

@login_required
def UserView(request):
    
    #get all artwork Listed by Artists
    artworks = Artwork.objects.all()

    #search query
    search_query = request.GET.get('search', '')
    if search_query:
        artworks = artworks.filter(title__icontains=search_query)
            
    return render(request, 'appln/UserHomePage.html', {'artworks': artworks, 'search_query':search_query})


def search_suggestions(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and 'term' in request.GET:

        search_term = request.GET.get('term', '')
        artworks = Artwork.objects.filter(title__icontains=search_term)
        suggestions = list(artworks.values('title'))
        return JsonResponse(suggestions, safe=False)

@login_required  # Ensure the user is logged in before allowing logout
def custom_logout(request):
    # Log the user out
    logout(request)
    
    # Clear the session
    request.session.flush()
    
    # Redirect to the login page (adjust the URL name as needed)
    return redirect('home')


from django.shortcuts import render, redirect, get_object_or_404
from .forms import ArtistProfileForm
from .models import ArtistProfile, Artist  # Import the necessary models

def view_profile(request):
    # Replace 'Artist1' with how you're determining the artist
    # e.g., you can use request.user.username, or some other logic
    artist = get_object_or_404(Artist, username=request.user)  # Example, adjust as per your case

    try:
        # Get the current artist's profile if it exists
        artist_profile = ArtistProfile.objects.get(artist=artist)
        
    except ArtistProfile.DoesNotExist:
        artist_profile = None

    #messages.success(request, 'Your profile has been updated successfully!')
    #messages.error(request, 'An error occurred while updating your profile.')
    #messages.warning(request, 'Please check the information you provided.')
    messages.info(request, 'Your changes have been saved.')

    return render(request, 'appln/artist_profile_form.html', {'artist_profile': artist_profile})
