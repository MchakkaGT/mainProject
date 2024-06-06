from django.shortcuts import render

def home(request):
    # Your logic for the Home view
    return render(request, 'polls/home.html')

def restaurant_search(request):
    # Your logic for the Restaurant Search view
    return render(request, 'polls/restaurant_search.html')

def geolocation(request):
    # Your logic for the Geolocation view
    return render(request, 'polls/geolocation.html')

def favorites(request):
    # Your logic for the Favorites view
    return render(request, 'polls/favorites.html')
