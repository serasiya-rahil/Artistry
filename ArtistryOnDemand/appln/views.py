from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate  
from .forms import CustomUserSignupForm, ArtistSignupForm, ArtistLoginForm
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from .models import Artist
from django.contrib.auth.decorators import login_required



#view for default home page
def home(request):
    return render(request, 'appln/index.html')

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
    # Render the login page template
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Log the user in
            login(request, user)
            return redirect('home')  
        else:
            # Invalid login
            messages.error(request, 'Invalid username or password.')
            return render(request, 'appln/login.html') 
    else:
        return render(request, 'appln/login.html')
    

def artist_signup(request):
    if request.method == 'POST':
        form = ArtistSignupForm(request.POST)
        if form.is_valid():
            artist = form.save()
            # Log the user in after signup using their username
            user = User.objects.get(username=artist.username)
            login(request, user)
            return redirect('home')  # Redirect to a success page
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
    return render(request, 'appln/artistDashboard.html')