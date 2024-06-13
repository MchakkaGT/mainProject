import time

import requests
from django.shortcuts import render
from .forms import RestaurantSearchForm


def home(request):
    # Your logic for the Home view
    return render(request, 'polls/home.html')


def restaurant_search(request):
    details = None
    if request.method == 'POST':
        form = RestaurantSearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            details = get_restaurant_details(query)

    else:
        form = RestaurantSearchForm()

    return render(request, 'polls/restaurant_search.html', {'form': form, 'details': details})


def get_restaurant_details(query):
    api_key = 'AIzaSyABdQf3ttPoUcYqIFNhRzgL3V-zOBNbUx0'
    base_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'

    params = {
        'query': query,
        'key': api_key
    }

    response = requests.get(base_url, params=params)
    result = response.json()

    restaurants = []

    if result.get('status') == 'OK' and 'results' in result:
        candidates = result.get('results', [])[:10]
        print(candidates)

        for candidate in candidates:
            place_id = candidate.get('place_id')
            if place_id:
                detail_url = 'https://maps.googleapis.com/maps/api/place/details/json'
                detail_params = {
                    'place_id': place_id,
                    'fields': 'name,formatted_address,rating,opening_hours,types,',
                    'key': api_key
                }
                detail_response = requests.get(detail_url, params=detail_params)
                place_details = detail_response.json().get('result', {})
                print(place_details)

                if 'restaurant' in place_details.get('types', []):
                    restaurants.append(place_details)

    return restaurants

def geolocation(request):
    # Your logic for the Geolocation view
    return render(request, 'polls/geolocation.html')


def favorites(request):
    # Your logic for the Favorites view
    return render(request, 'polls/favorites.html')
