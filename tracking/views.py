"""WatchEntry, Review CRUD ve AJAX endpoint'leri."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from movies.models import Movie

from .forms import ReviewForm, WatchEntryForm
from .models import Review, ReviewLike, WatchEntry


@login_required
@require_POST
def update_watch_entry_view(request, media_type, tmdb_id):
    movie = get_object_or_404(Movie, tmdb_id=tmdb_id, media_type=media_type)
    entry, _ = WatchEntry.objects.get_or_create(
        user=request.user, movie=movie,
        defaults={'status': WatchEntry.Status.WANT},
    )
    form = WatchEntryForm(request.POST, instance=entry)
    if form.is_valid():
        form.save()
        messages.success(request, "The list has been updated.")
    else:
        messages.error(request, "Invalid data.")
    return redirect('movies:detail', media_type=media_type, tmdb_id=tmdb_id)


@login_required
@require_POST
def delete_watch_entry_view(request, media_type, tmdb_id):
    movie = get_object_or_404(Movie, tmdb_id=tmdb_id, media_type=media_type)
    deleted, _ = WatchEntry.objects.filter(user=request.user, movie=movie).delete()
    if deleted:
        messages.success(request, "The item has been removed from the list.")
    return redirect('movies:detail', media_type=media_type, tmdb_id=tmdb_id)


@login_required
@require_POST
def save_review_view(request, media_type, tmdb_id):
    movie = get_object_or_404(Movie, tmdb_id=tmdb_id, media_type=media_type)
    existing = Review.objects.filter(user=request.user, movie=movie).first()
    form = ReviewForm(request.POST, instance=existing)
    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.movie = movie
        review.save()
        messages.success(request, "The review has been saved.")
    else:
        for field, errs in form.errors.items():
            for err in errs:
                messages.error(request, f"{field}: {err}")
    return redirect('movies:detail', media_type=media_type, tmdb_id=tmdb_id)


@login_required
@require_POST
def delete_review_view(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    media_type = review.movie.media_type
    tmdb_id = review.movie.tmdb_id
    review.delete()
    messages.success(request, "The review has been deleted.")
    return redirect('movies:detail', media_type=media_type, tmdb_id=tmdb_id)


@login_required
@require_POST
def toggle_review_like_view(request, review_id):
    """AJAX: review beğen/beğenmekten vazgeç. JSON döndürür."""
    review = get_object_or_404(Review, id=review_id)
    like, created = ReviewLike.objects.get_or_create(user=request.user, review=review)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'count': review.likes.count()})
