"""Movies admin — Movie ve Genre için Django admin kayıtları."""
from django.contrib import admin

from .models import Genre, Movie


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """TMDB film türleri için admin görünümü."""
    list_display = ['name', 'tmdb_id']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """Film ve dizi kayıtları için admin görünümü."""
    list_display = ['title', 'media_type', 'release_date', 'vote_average', 'fetched_at']
    list_filter = ['media_type', 'genres', 'release_date']
    search_fields = ['title', 'original_title']
    filter_horizontal = ['genres']
    readonly_fields = ['fetched_at']
    date_hierarchy = 'release_date'
