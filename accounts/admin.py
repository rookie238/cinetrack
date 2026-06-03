"""Accounts admin  Profile ve Follow için Django admin kayıtları."""
from django.contrib import admin

from .models import Follow, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Kullanıcı profilleri için admin görünümü."""
    list_display = ['user', 'location', 'created_at']
    search_fields = ['user__username', 'user__email', 'location']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Kullanıcı-kullanıcı takip ilişkileri için admin görünümü."""
    list_display = ['follower', 'following', 'created_at']
    search_fields = ['follower__username', 'following__username']
    list_filter = ['created_at']
    autocomplete_fields = ['follower', 'following']
