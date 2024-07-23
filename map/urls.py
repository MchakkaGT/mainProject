from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


app_name = "map"


urlpatterns = [
   path('', views.map_view, name='map_view'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

