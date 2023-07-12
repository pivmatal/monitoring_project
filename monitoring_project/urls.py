"""monitoring_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path
from django.conf.urls import include

from monitoring import views
from selfcare import views as selfcare

urlpatterns = [
    path('', views.monitoring_view, name='index'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('selfcare/', selfcare.selfcare, name='index'),
    path('greetings/', selfcare.mart),
    path('ui/', selfcare.ui),
    path(r'selfcare/<int:pk>', selfcare.device_view, name='device'),
]
