from django.shortcuts import render
from django.http import HttpResponse

#view for default home page
def home(request):
    return render(request, 'home.html')

#
def login(request):
    return render(request, 'login.html')

