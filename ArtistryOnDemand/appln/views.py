from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate  # Ensure correct import
from .forms import CustomUserSignupForm
from django.contrib import messages
from django.http import HttpResponse

#view for default home page
def home(request):
    return render(request, 'appln/home.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('home')
    else:
        form = CustomUserSignupForm()
    return render(request, 'appln/signup.html', {'form': form})

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
    




