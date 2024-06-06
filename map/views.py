from django.shortcuts import render

# Create your views here.
from django.shortcuts import render


def map_view(request):
    return render(request, 'map/map.html')
