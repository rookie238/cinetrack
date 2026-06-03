"""Movie views — TMDB search ve film detayı."""
import requests
from django.http import Http404
from django.shortcuts import render

from tracking.forms import ReviewForm, WatchEntryForm
from tracking.models import Review, WatchEntry

from . import services, tmdb


def search_view(request):
    """TMDB üzerinden film/dizi arar, sonuçları kart şeklinde gösterir."""
    query = request.GET.get('q', '').strip()
    page_param = request.GET.get('page', '1')

    try:
        page = max(1, int(page_param))
    except (TypeError, ValueError):
        page = 1

    results = []
    total_pages = 0
    error = None

    if query:
        try:
            data = tmdb.search_multi(query, page=page)
            for item in data.get('results', []):
                media_type = item.get('media_type')
                if media_type not in ('movie', 'tv'):
                    continue
                results.append({
                    'id': item['id'],
                    'media_type': media_type,
                    'title': item.get('title') or item.get('name', ''),
                    'release_date': item.get('release_date') or item.get('first_air_date', ''),
                    'poster_path': item.get('poster_path'),
                    'overview': item.get('overview', ''),
                })
            total_pages = min(data.get('total_pages', 1), 500)
        except requests.RequestException:
            error = "TMDB could not be reached, please try again later."

    return render(request, 'movies/search.html', {
        'query': query,
        'results': results,
        'page': page,
        'total_pages': total_pages,
        'error': error,
    })


def movie_detail_view(request, media_type, tmdb_id):
    """Film/dizi detayı + kullanıcının watch entry/review + tüm review'lar."""
    if media_type not in ('movie', 'tv'):
        raise Http404("Invalid media type")

    try:
        movie = services.get_or_fetch_movie(tmdb_id, media_type)
    except requests.RequestException:
        raise Http404("Movie/series could not be fetched from TMDB")

    user_watch_entry = None
    user_review = None
    other_reviews_qs = Review.objects.filter(movie=movie).select_related('user', 'user__profile')

    if request.user.is_authenticated:
        user_watch_entry = WatchEntry.objects.filter(user=request.user, movie=movie).first()
        user_review = Review.objects.filter(user=request.user, movie=movie).first()
        other_reviews_qs = other_reviews_qs.exclude(user=request.user)

    return render(request, 'movies/detail.html', {
        'movie': movie,
        'user_watch_entry': user_watch_entry,
        'user_review': user_review,
        'other_reviews': other_reviews_qs.order_by('-created_at'),
        'watch_form': WatchEntryForm(instance=user_watch_entry),
        'review_form': ReviewForm(instance=user_review),
    })
