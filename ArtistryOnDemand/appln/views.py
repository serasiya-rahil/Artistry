from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserSignupForm, ArtistSignupForm, ArtistLoginForm, ArtworkForm, EditArtworkForm
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from .models import Artist, Artwork
from django.contrib.auth.decorators import login_required
import os

def home(request):
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

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
         
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')  
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

            try:
                artist = Artist.objects.get(username=username)
            except Artist.DoesNotExist:
                messages.error(request, "Artist does not exist.")
                return render(request, 'appln/artist_login.html', {'form': form})

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("artistDashboard")
            else:
                messages.error(request, "Invalid credentials. Please try again.")
    else:
        form = ArtistLoginForm()

    return render(request, 'appln/artist_login.html', {'form': form})

@login_required
def artistDashboard(request):
    try:
        artist = Artist.objects.get(username=request.user)
        
        artworks = Artwork.objects.filter(artist=artist)
        total_artworks = artworks.count()
        
        search_query = request.GET.get('search', '')
        if search_query:
            artworks = artworks.filter(title__icontains=search_query)
    except Artist.DoesNotExist:
        artworks = []
        artist = None

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
    artwork = get_object_or_404(Artwork, artwork_id=artwork_id, artist__username=request.user)

    old_image_path = artwork.image_path.path if artwork.image_path else None
    old_video_path = artwork.video_path.path if artwork.video_path else None

    if request.method == 'POST':
        form = EditArtworkForm(request.POST, request.FILES, instance=artwork)
        if form.is_valid():
            if 'image_path' in request.FILES and old_image_path:
                if os.path.isfile(old_image_path):
                    os.remove(old_image_path)

            if 'video_path' in request.FILES and old_video_path:
                if os.path.isfile(old_video_path):
                    os.remove(old_video_path)  

            form.save()
            return redirect('artistDashboard')
    else:
        form = EditArtworkForm(instance=artwork)

    return render(request, 'appln/edit_artwork.html', {
        'form': form,
        'artwork': artwork,
    })

@login_required 
def custom_logout(request):
    logout(request)
    request.session.flush()
    
    return redirect('home')