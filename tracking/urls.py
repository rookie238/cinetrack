from django.urls import path

from . import views

app_name = 'tracking'

urlpatterns = [
    path('watch/<str:media_type>/<int:tmdb_id>/', views.update_watch_entry_view, name='watch_update'),
    path('watch/<str:media_type>/<int:tmdb_id>/delete/', views.delete_watch_entry_view, name='watch_delete'),
    path('review/<str:media_type>/<int:tmdb_id>/', views.save_review_view, name='review_save'),
    path('review/<int:review_id>/delete/', views.delete_review_view, name='review_delete'),
    path('review/<int:review_id>/like/', views.toggle_review_like_view, name='review_like'),
]
