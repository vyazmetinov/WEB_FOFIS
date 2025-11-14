"""
API URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FlightCaseViewSet

router = DefaultRouter()
router.register(r'flight-cases', FlightCaseViewSet, basename='flightcase')

urlpatterns = [
    path('', include(router.urls)),
]

