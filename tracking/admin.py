"""Tracking admin — WatchEntry, Review, ReviewLike, Comment için admin kayıtları."""
from django.contrib import admin

from .models import Comment, Review, ReviewLike, WatchEntry


@admin.register(WatchEntry)
class WatchEntryAdmin(admin.ModelAdmin):
    """Kullanıcıların izleme listesi kayıtları için admin görünümü."""
    list_display = ['user', 'movie', 'status', 'rating', 'updated_at']
    list_filter = ['status', 'rating', 'updated_at']
    search_fields = ['user__username', 'movie__title']
    autocomplete_fields = ['user', 'movie']
    readonly_fields = ['added_at', 'updated_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Yorumlar için admin görünümü."""
    list_display = ['user', 'movie', 'rating', 'like_count', 'comment_count', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'movie__title', 'text']
    autocomplete_fields = ['user', 'movie']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    """Yorum beğenileri için admin görünümü."""
    list_display = ['user', 'review', 'created_at']
    search_fields = ['user__username']
    autocomplete_fields = ['user', 'review']
    list_filter = ['created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Review altı yorumlar için admin görünümü."""
    list_display = ['user', 'review', 'short_text', 'created_at']
    search_fields = ['user__username', 'text']
    autocomplete_fields = ['user', 'review']
    list_filter = ['created_at']

    @admin.display(description='Yorum')
    def short_text(self, obj):
        """Listede uzun yorumları 60 karaktere kadar göster."""
        return obj.text[:60] + ('...' if len(obj.text) > 60 else '')
