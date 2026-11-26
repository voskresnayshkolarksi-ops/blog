from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'users'
urlpatterns = [
    path('logout/', LogoutView.as_view(http_method_names=['post']), name='logout'),
    path('', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
]
