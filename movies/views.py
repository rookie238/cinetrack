"""Movie views — TMDB search ve film detayı."""
import requests
from django.http import Http404
from django.shortcuts import render

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
                # Sadece film/dizi göster (kişi vs. hariç)
                if item.get('media_type') in ('movie', 'tv'):
                    results.append(item)
            # TMDB sayfalama max 500'de durur
            total_pages = min(data.get('total_pages', 1), 500)
        except requests.RequestException:
            error = "TMDB'ye ulaşılamadı, lütfen biraz sonra tekrar dene."

    return render(request, 'movies/search.html', {
        'query': query,
        'results': results,
        'page': page,
        'total_pages': total_pages,
        'error': error,
    })


def movie_detail_view(request, media_type, tmdb_id):
    """Film/dizi detayı. DB'de yoksa veya cache eskise TMDB'den çeker."""
    if media_type not in ('movie', 'tv'):
        raise Http404("Geçersiz medya tipi")

    try:
        movie = services.get_or_fetch_movie(tmdb_id, media_type)
    except requests.RequestException:
        raise Http404("Film/dizi TMDB'den çekilemedi")

    return render(request, 'movies/detail.html', {
        'movie': movie,
    })
