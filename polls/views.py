
import requests
from django.shortcuts import render
from .forms import RestaurantSearchForm
from datetime import datetime


# View function to call on the home page
def home(request):
    return render(request, 'polls/home.html')


# View function that is used to call on the restaurant_search page
def restaurant_search(request):
    if request.method == 'POST':
        query = request.POST.get('query', '')
        rating = request.POST.get('rating')
        max_price = request.POST.get('max_price')
        distance = request.POST.get('distance')

        # Convert distance to meters if specified
        if distance:
            distance = int(distance) * 1000

        details = get_restaurant_details(query, rating, max_price, distance)
        return render(request, 'polls/restaurant_search.html', {'details': details})
    return render(request, 'polls/restaurant_search.html', {})


# Function to retrieve restaurants sorted by distance
def get_restaurant_details(query, rating=None, max_price=None, distance=None):
    api_key = 'AIzaSyABdQf3ttPoUcYqIFNhRzgL3V-zOBNbUx0'
    base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'

    params = {
        'keyword': query,
        'key': api_key,
        'type': 'restaurant',
        'location': '34.19656985679236, -84.22358663254866',
        'radius': distance or 5000
    }

    response = requests.get(base_url, params=params)
    result = response.json()

    restaurants = []
    size = 0

    if result.get('status') == 'OK' and 'results' in result:
        candidates = result.get('results', [])[:]

        for candidate in candidates:
            is_restaurant = 'restaurant' in candidate.get('types', [])

            if candidate.get('price_level') and max_price:
                is_max = float(candidate.get('price_level')) <= float(max_price)
            else:
                is_max = True

            if candidate.get('rating') and rating:
                candidate_rating = float(candidate.get('rating'))
                rating_value = float(rating)
                is_rating = candidate_rating >= rating_value
            else:
                is_rating = True

            if is_restaurant and size < 9 and is_rating and is_max:
                print(candidate)

                # Get restaurant details
                candidate_details = {
                    'name': candidate.get('name'),
                    'address': candidate.get('formatted_address'),
                    'rating': candidate.get('rating'), 'today_hours': None,
                    'image_url': get_image(candidate, api_key),
                    'open_hours': None,
                    'number': None,
                }

                # Get specific details
                details = get_details(candidate, api_key, candidate.get('place_id'))
                candidate_details['open_hours'] = details.get('open_hours')
                candidate_details['number'] = details.get('number')
                candidate_details['address'] = details.get('address')

                restaurants.append(candidate_details)
                size += 1

    return restaurants if restaurants else None


def get_image(candidate, api_key):
    photo_base_url = 'https://maps.googleapis.com/maps/api/place/photo'

    if 'photos' in candidate and len(candidate['photos']) > 0:
        photo_reference = candidate['photos'][0]['photo_reference']
        photo_url = f'{photo_base_url}?maxwidth=400&photoreference={photo_reference}&key={api_key}'
        return photo_url
    else:
        return None


def get_details(candidate, api_key, place_id):
    place_details_url = 'https://maps.googleapis.com/maps/api/place/details/json'

    if place_id:
        details_params = {
            'place_id': place_id,
            'key': api_key,
            'fields': 'opening_hours,formatted_phone_number,formatted_address'
        }

        details_response = requests.get(place_details_url, params=details_params)
        details_result = details_response.json()

        if details_result.get('status') == 'OK' and 'result' in details_result:
            detailed_info = details_result['result']
            opening_hours = detailed_info.get('opening_hours', {})

            place_details = {
                'open_hours': None,
                'number': detailed_info.get('formatted_phone_number'),
                'address': detailed_info.get('formatted_address'),
            }

            if opening_hours:
                weekday_text = opening_hours.get('weekday_text', [])

                if weekday_text:
                    current_day_index = datetime.now().weekday()
                    today_hours = weekday_text[current_day_index]
                    timings_only = today_hours.split(': ', 1)[1].strip()
                    place_details['open_hours'] = timings_only

        return place_details


def geolocation(request):
    return render(request, 'polls/geolocation.html')


def favorites(request):
    return render(request, 'polls/favorites.html')
