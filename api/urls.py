"""API URL'leri — DRF Router otomatik tüm RESTful endpoint'leri üretir."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('movies', views.MovieViewSet, basename='movie')
router.register('watch-entries', views.WatchEntryViewSet, basename='watchentry')
router.register('reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),  # browsable API için login/logout
]
