"""TMDB API client - themoviedb.org REST API wrapper."""
import requests
from django.conf import settings


def _headers():
    return {
        'Authorization': f'Bearer {settings.TMDB_API_TOKEN}',
        'accept': 'application/json',
    }


def _get(endpoint, params=None):
    """TMDB API'ye GET isteği at, JSON döndür."""
    url = f'{settings.TMDB_BASE_URL}{endpoint}'
    response = requests.get(url, headers=_headers(), params=params or {}, timeout=10)
    response.raise_for_status()
    return response.json()


# Arama
def search_multi(query, page=1):
    """Hem film hem diziyi tek seferde arar."""
    return _get('/search/multi', {'query': query, 'page': page, 'language': 'en-US'})


# Detaylar
def get_movie_details(tmdb_id):
    return _get(f'/movie/{tmdb_id}', {'language': 'en-US'})


def get_tv_details(tmdb_id):
    return _get(f'/tv/{tmdb_id}', {'language': 'en-US'})


# Popülerler
def get_popular_movies(page=1):
    return _get('/movie/popular', {'page': page, 'language': 'en-US'})


def get_popular_tv(page=1):
    return _get('/tv/popular', {'page': page, 'language': 'en-US'})


# Türler
def get_movie_genres():
    return _get('/genre/movie/list', {'language': 'en-US'}).get('genres', [])


def get_tv_genres():
    return _get('/genre/tv/list', {'language': 'en-US'}).get('genres', [])
