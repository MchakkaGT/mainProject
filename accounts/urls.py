from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

from .views import SignUpView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("logout/", views.logout_view, name="logout")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
