from django.urls import path
from . import views


app_name = "polls"
urlpatterns = [
    path('', views.home, name='home'),
    path('restaurants_search/', views.restaurant_search, name='restaurant_search'),
    path('geolocation/', views.geolocation, name='geolocation'),
    path('favorites/', views.favorites, name='favorites'),
]