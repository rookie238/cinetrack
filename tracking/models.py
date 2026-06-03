from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class WatchEntry(models.Model):
   

    class Status(models.TextChoices):
        WANT = 'want', 'Want to Watch'
        WATCHING = 'watching', 'Watching'
        WATCHED = 'watched', 'Watched'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='watch_entries',
    )
    movie = models.ForeignKey(
        'movies.Movie',
        on_delete=models.CASCADE,
        related_name='watch_entries',
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.WANT,
    )
    rating = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="1-10 range rating (optional)",
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'movie'],
                name='unique_watch_entry',
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['movie']),
        ]
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.get_status_display()})"


class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    movie = models.ForeignKey(
        'movies.Movie',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    text = models.TextField(max_length=5000)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'movie'],
                name='unique_user_movie_review',
            ),
        ]
        indexes = [
            models.Index(fields=['movie', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.rating}/10)"

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()


class ReviewLike(models.Model):
    """Bir kullanıcının bir review'a beğenisi."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_likes',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'review'],
                name='unique_review_like',
            ),
        ]
        indexes = [
            models.Index(fields=['review']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} ♥ {self.review}"


class Comment(models.Model):
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['review', 'created_at']),
        ]
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username}: {self.text[:50]}..."