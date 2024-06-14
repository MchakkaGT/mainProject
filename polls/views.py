import time

import requests
from django.shortcuts import render
from .forms import RestaurantSearchForm

# View function to call on the home page
def home(request):
    # Your logic for the Home view
    return render(request, 'polls/home.html')


# View function that is used to call on the restaurant_search page
def restaurant_search(request):
    details = None

    # If searchbar returns a query (user input) then we use this if statement
    if request.method == 'POST':
        form = RestaurantSearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            details = get_restaurant_details(query)
    else:
        form = RestaurantSearchForm()

    return render(request, 'polls/restaurant_search.html', {'form': form, 'details': details})


# This function is mainly utilized to connect with the Google API and pull information about resturants.
def get_restaurant_details(query):
    api_key = 'AIzaSyABdQf3ttPoUcYqIFNhRzgL3V-zOBNbUx0'
    base_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'

    params = {
        'query': query,
        'key': api_key
    }

    # Pulls any information related to the query and converts it into a readable form.
    response = requests.get(base_url, params=params)
    result = response.json()

    restaurants = []

    # Used to iterate through the json file and put restaurants into an array which can be returned
    # back to the restaurant_search page
    if result.get('status') == 'OK' and 'results' in result:
        candidates = result.get('results', [])[:9]

        # Takes in the first 10 candidates and iterates through them to make sure they are
        # restaurants and puts them into an array with the details requested for through
        # parameters.
        for candidate in candidates:
            place_id = candidate.get('place_id')
            if place_id:
                detail_url = 'https://maps.googleapis.com/maps/api/place/details/json'
                detail_params = {
                    'place_id': place_id,
                    'fields': 'name,types,formatted_address,rating,photos',
                    'key': api_key
                }
                detail_response = requests.get(detail_url, params=detail_params)
                place_details = detail_response.json().get('result', {})

                if 'restaurant' in place_details.get('types', []):

                    # Gets photos if available
                    photos = place_details.get('photos', [])
                    if photos:
                        photo_ref = photos[0]['photo_reference']
                        image_url = get_image_url(photo_ref, api_key)
                        place_details['image_url'] = image_url

                    restaurants.append(place_details)

    if len(restaurants) == 0:
        return None
    else:
        return restaurants


def get_image_url(photo_reference, api_key):
    photos_url = 'https://maps.googleapis.com/maps/api/place/photo'
    photos_params = {
        'photoreference': photo_reference,
        'maxwidth': 400,
        'key': api_key
    }
    response = requests.get(photos_url, params=photos_params)
    return response.url

def geolocation(request):
    # Your logic for the Geolocation view
    return render(request, 'polls/geolocation.html')


def favorites(request):
    # Your logic for the Favorites view
    return render(request, 'polls/favorites.html')
