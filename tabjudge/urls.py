from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework import routers
from . import upViews


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'images', upViews.ImageViewSet)

urlpatterns = [
    # APIのルート
    path('api/', include(router.urls)),
]
