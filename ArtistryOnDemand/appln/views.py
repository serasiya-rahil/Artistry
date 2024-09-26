from django.shortcuts import render
from django.http import HttpResponse

#view for default home page
def home(request):
    return render(request, 'appln/home.html')


