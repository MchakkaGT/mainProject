
from rest_framework import serializers
from .models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'place_id', 'name', 'address', 'rating', 'open_hours', 'number', 'latitude',
                  'longitude', 'image_url']
