from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('appln/',include('appln.urls')),
    path('', include('appln.urls')),
]
