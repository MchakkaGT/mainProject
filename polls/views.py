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
            print(details)
    else:
        form = RestaurantSearchForm()

    return render(request, 'polls/restaurant_search.html', {'form': form, 'details': details})


def get_restaurant_details(query):
    api_key = 'AIzaSyABdQf3ttPoUcYqIFNhRzgL3V-zOBNbUx0'
    url = f'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={query}&inputtype=textquery&fields=name,formatted_address,rating,place_id&key={api_key}'
    response = requests.get(url)
    result = response.json()

    restaurants = []

    if result['status'] == 'OK' and result['candidates']:
        for candidate in result['candidates'][:10]:
            place_id = candidate['place_id']

            detail_url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,geometry,website,rating,types&key={api_key}'
            detail_response = requests.get(detail_url)
            place_details = detail_response.json().get('result', {})

            if 'restaurant' in place_details.get('types', []):
                restaurants.append(place_details)

        return restaurants
    return None

def geolocation(request):
    # Your logic for the Geolocation view
    return render(request, 'polls/geolocation.html')


def favorites(request):
    # Your logic for the Favorites view
    return render(request, 'polls/favorites.html')
