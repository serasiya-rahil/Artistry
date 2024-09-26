from django.shortcuts import render
from django.http import HttpResponse

#view for default home page
def home(request):
    return render(request, 'appln/home.html')

def singup(request):
    # Render the login page template
    return render(request,'appln/signup.html')

def login(request):
    # Render the login page template
    return render(request,'appln/login.html')

    




