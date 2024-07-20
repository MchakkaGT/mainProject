import requests
import json
from django.shortcuts import render
from datetime import datetime
from django.http import JsonResponse

from polls.models import Favorite


latitude = None
longitude = None


# View function to call on the home page
def home(request):
    return render(request, 'polls/home.html')


def details(request, place_id):
    return render(request, 'polls/details.html', {'place_id': place_id})


# Gets user location
def get_location(request):

    if request.method == 'POST':
        global latitude, longitude

        try:
            data = json.loads(request.body)
            latitude = data['lat']
            longitude = data['lng']

            return JsonResponse({"message": "Successfully Sent"})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)


# View function that is used to call on the restaurant_search page
def restaurant_search(request):
    # When submit button is clicked, the if statement gets the values in each field.
    if request.method == 'POST':
        global latitude, longitude
        if request.POST.get('query'):
            query = request.POST.get('query', '')
            rating = request.POST.get('rating')
            max_price = request.POST.get('max_price')
            distance = request.POST.get('distance')

            location = f"{latitude}, {longitude}"


            # Convert distance to meters if specified
            if distance:
                distance = int(distance) * 1000

            # Gets data from the API and saves them in a variable.
            details = get_restaurant_details(query, rating, max_price, distance, location)
            details_json = json.dumps(details)

            return render(request, 'polls/restaurant_search.html', {'mapDetails': details_json, 'details': details})

        elif request.body:
            data = json.loads(request.body)
            places = data.get('places', [])
            # print(places)
            return render(request, 'polls/restaurant_search.html', {'places': places})

    return render(request, 'polls/restaurant_search.html', {})


# Function to retrieve restaurants sorted by distance
def get_restaurant_details(query, rating=None, max_price=None, distance=None, location='33.77683196783757, -84.39622529694923'):
    api_key = 'AIzaSyABdQf3ttPoUcYqIFNhRzgL3V-zOBNbUx0'
    base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'

    # Parameters when calling the API for restaurant information.
    params = {
        'keyword': query,
        'key': api_key,
        'type': 'restaurant',
        'location': location, # set to coords when data is formatted correctly
        'radius': distance or 5000
    }

    response = requests.get(base_url, params=params)
    result = response.json()

    restaurants = []
    size = 0

    # If the API returns restaurant data, I enter the if statement and get the data I want.
    if result.get('status') == 'OK' and 'results' in result:
        candidates = result.get('results', [])[:]

        for candidate in candidates:
            is_restaurant = 'restaurant' in candidate.get('types', [])

            # The if statement works to filter out certain restaurants is the user asks for
            # specific restaurant criteria.
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
                # Creates an object which contains all the details.
                candidate_details = {
                    'place_id': candidate.get('place_id'),
                    'name': candidate.get('name'),
                    'address': candidate.get('formatted_address'),
                    'rating': candidate.get('rating'),
                    'today_hours': None,
                    'image_url': get_image(candidate, api_key),
                    'open_hours': None,
                    'number': None,
                    'lat': candidate['geometry']['location']['lat'],
                    'lng': candidate['geometry']['location']['lng'],
                }

                # Get specific details from other APIs within Google.
                details = get_details(candidate, api_key, candidate.get('place_id'))
                candidate_details['open_hours'] = details.get('open_hours')
                candidate_details['number'] = details.get('number')
                candidate_details['address'] = details.get('address')
                candidate_details['reviews'] = details.get('reviews')
                # print(details.get('reviews'))

                restaurants.append(candidate_details)
                size += 1

    return restaurants if restaurants else None


# This function is used to call the photo API to retrieve a photo of the restaurant.
def get_image(candidate, api_key):
    photo_base_url = 'https://maps.googleapis.com/maps/api/place/photo'

    if 'photos' in candidate and len(candidate['photos']) > 0:
        photo_reference = candidate['photos'][0]['photo_reference']
        photo_url = f'{photo_base_url}?maxwidth=400&photoreference={photo_reference}&key={api_key}'
        return photo_url
    else:
        return None


# This function is used to get more specific data about a certain restaurant.
def get_details(candidate, api_key, place_id):
    place_details_url = 'https://maps.googleapis.com/maps/api/place/details/json'

    if place_id:

        # inputs to the API to get specific results.
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

            # Creates an object which contains the details we asked for.
            place_details = {
                'open_hours': None,
                'number': detailed_info.get('formatted_phone_number'),
                'address': detailed_info.get('formatted_address'),
                'reviews': detailed_info.get('reviews')
            }
            # print(detailed_info.get('reviews'))

            # Logic to display current days opening hours.
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


# Is a RestAPI call to Django Database to post data about a user's favorite restaurant.
def add_to_favorites(request):
    # If the user calls the method we check to see if the user called a post method.
    if request.method == 'POST':
        user = request.user
        data = request.POST

        # Once we check that there is a logged-in user we get the data of the restaurant he wants to save.
        try:
            place_id = data.get('place_id')
            name = data.get('name')
            address = data.get('address')
            open_hours = data.get('open_hours')
            number = data.get('number')
            rating = data.get('rating')
            latitude = float(data.get('latitude', 0))
            longitude = float(data.get('longitude', 0))
            image_url = data.get('image_url')

            # We check to make sure the user hasn't already saved this restaurant by checking its place_id.
            if not Favorite.objects.filter(user=user, place_id=place_id).exists():
                favorite = Favorite(
                    user=user,
                    place_id=place_id,
                    name=name,
                    address=address,
                    open_hours=open_hours,
                    number=number,
                    rating=rating,
                    latitude=latitude,
                    longitude=longitude,
                    image_url=image_url
                )
                favorite.save()

                return JsonResponse({'status': 'success', 'message': 'Favorite added successfully.'})
            else:
                return JsonResponse({'status': 'info', 'message': 'Restaurant is already in favorites.'})

        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid data provided.'}, status=400)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Internal Server Error.'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


# Is a RestAPI call to Django Database to remove data about a certain user's favorite restaurant.
def remove_from_favorites(request):

    # Checks to see if the user calls a post method.
    if request.method == 'POST':
        place_id = request.POST.get('place_id')
        try:
            # It located the item the user wants to delete by searching for its place_id and then deletes
            # that data from the database for the specified user.
            favorite = Favorite.objects.get(user=request.user, place_id=place_id)
            favorite.delete()
            return JsonResponse({'message': 'Successfully removed from favorites.'}, status=200)
        except Favorite.DoesNotExist:
            return JsonResponse({'error': 'Favorite does not exist.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


# Is a RestAPI call to Django Database to fetch the place_ids of all the restaurants the user has saved.
def get_favorite_place_ids(request):
    if not request.user.is_authenticated:
        return JsonResponse([], safe=False)
    else:
        favorite_place_ids = list(Favorite.objects.filter(user=request.user).values_list('place_id', flat=True))
        return JsonResponse(favorite_place_ids, safe=False)


# Favorites page that displays the users favorite restaurant list.
def favorites(request):

    # Checks to see if the user is logged in. If not then he does not have access to adding to Favorites
    if not request.user.is_active:
        return render(request, 'polls/favorites.html')

    # Checks to see if the user has added any restaurants to favorites.
    elif Favorite.objects.filter(user=request.user) is None:
        return render(request, 'polls/favorites.html')

    # if the other statements are false, then the user is both logged in and has items so we return the
    # restaurant list as an object.
    else:
        favorite_restaurants = Favorite.objects.filter(user=request.user)
        favorites_dict = [
            {
                'name': favorite.name,
                'place_id': favorite.place_id,
                'address': favorite.address,
                'rating': favorite.rating,
                'open_hours': favorite.open_hours,
                'number': favorite.number,
                'latitude': favorite.latitude,
                'longitude': favorite.longitude,
                'image_url': favorite.image_url
            }
            for favorite in favorite_restaurants
        ]

        return render(request, 'polls/favorites.html', {'favorites': favorites_dict})
