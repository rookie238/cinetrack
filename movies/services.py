"""TMDB verilerini Movie modeline çeviren business logic."""
from datetime import datetime, timedelta

from django.utils import timezone

from . import tmdb
from .models import Genre, Movie


def _parse_date(date_str):
    """TMDB tarih formatından (YYYY-MM-DD) Python date'e çevir."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None


def save_genres_from_tmdb():
    """TMDB'den tüm film+dizi türlerini çek, DB'ye kaydet."""
    all_genres = tmdb.get_movie_genres() + tmdb.get_tv_genres()
    seen = set()
    count = 0
    for g in all_genres:
        if g['id'] in seen:
            continue
        seen.add(g['id'])
        Genre.objects.update_or_create(
            tmdb_id=g['id'],
            defaults={'name': g['name']},
        )
        count += 1
    return count


def save_movie_from_tmdb(tmdb_data, media_type):
    """TMDB dict'inden Movie objesi yaratır veya günceller."""
    if media_type == Movie.MediaType.MOVIE:
        title = tmdb_data.get('title') or tmdb_data.get('original_title', '')
        original_title = tmdb_data.get('original_title', '')
        release_date = _parse_date(tmdb_data.get('release_date'))
    else:  # TV
        title = tmdb_data.get('name') or tmdb_data.get('original_name', '')
        original_title = tmdb_data.get('original_name', '')
        release_date = _parse_date(tmdb_data.get('first_air_date'))

    movie, _created = Movie.objects.update_or_create(
        tmdb_id=tmdb_data['id'],
        media_type=media_type,
        defaults={
            'title': title,
            'original_title': original_title,
            'overview': tmdb_data.get('overview', ''),
            'poster_path': tmdb_data.get('poster_path') or '',
            'backdrop_path': tmdb_data.get('backdrop_path') or '',
            'release_date': release_date,
            'runtime': tmdb_data.get('runtime'),
            'vote_average': tmdb_data.get('vote_average'),
        },
    )

    genre_ids = []
    if 'genres' in tmdb_data:
        genre_ids = [g['id'] for g in tmdb_data['genres']]
    elif 'genre_ids' in tmdb_data:
        genre_ids = tmdb_data['genre_ids']

    if genre_ids:
        genres = Genre.objects.filter(tmdb_id__in=genre_ids)
        movie.genres.set(genres)

    return movie


def get_or_fetch_movie(tmdb_id, media_type):
    """
    Önce DB'den bak, yoksa veya 7 günden eskiyse TMDB'den taze çek.
    Cache stratejisi: her sayfa yüklemesinde API spam yapmıyoruz.
    """
    try:
        movie = Movie.objects.get(tmdb_id=tmdb_id, media_type=media_type)
        if movie.fetched_at > timezone.now() - timedelta(days=7):
            return movie
    except Movie.DoesNotExist:
        pass

    if media_type == Movie.MediaType.MOVIE:
        data = tmdb.get_movie_details(tmdb_id)
    else:
        data = tmdb.get_tv_details(tmdb_id)

    return save_movie_from_tmdb(data, media_type)
