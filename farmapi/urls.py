"""
URL configuration for farmapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import RegisterView, LogoutView, LoginView, ProfileView


urlpatterns = [
    path('admin/', admin.site.urls),

    # --- Auth ---
    # register: create a new user (public).
    # login:    phone_number + password -> { access, refresh } tokens (digits normalized).
    # refresh:  swap a valid refresh token for a fresh access token.
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('api/auth/me/', ProfileView.as_view(), name='me'),

    # --- App resources (all require a valid access token) ---
    path('api/', include('farm.urls')),
    path('api/', include('crops.urls')),
    path('api/', include('tasks.urls')),
    path('api/', include('budgeting.urls')),

    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
]
