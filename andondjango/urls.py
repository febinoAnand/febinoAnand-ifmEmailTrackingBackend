"""
URL configuration for andondjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
from django.contrib.staticfiles.urls import staticfiles_urlpatterns



urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('emailtracking/', include('emailtracking.urls')),
    path('smsgateway/', include('smsgateway.urls')),
    path('pushnotification/', include('pushnotification.urls')),
    path('Userauth/', include('Userauth.urls')),
    path('app/', include('Userauth.urls')),
    path('settings/', include('settings.urls')),
    path('', admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()

