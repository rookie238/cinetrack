from django.urls import path

from . import views

app_name = 'movies'

urlpatterns = [
    path('search/', views.search_view, name='search'),
    path('<str:media_type>/<int:tmdb_id>/', views.movie_detail_view, name='detail'),
]
