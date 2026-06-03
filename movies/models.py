from django.db import models

# Create your models here.
from django.db import models


class Genre(models.Model):
    """TMDB film türleri (Action, Drama, Sci-Fi, vb.)"""
    tmdb_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Movie(models.Model):
    """
    TMDB'den çekip cache'lediğimiz film/dizi kayıtları.
    Bir kullanıcı listeye eklediğinde, film DB'mizde yoksa TMDB'den
    çekilip burada saklanır. Sonraki erişimlerde DB'den okuruz.
    """

    class MediaType(models.TextChoices):
        MOVIE = 'movie', 'Movie'
        TV = 'tv', 'Series'

    tmdb_id = models.IntegerField()
    media_type = models.CharField(
        max_length=10,
        choices=MediaType.choices,
        default=MediaType.MOVIE,
    )
    title = models.CharField(max_length=255)
    original_title = models.CharField(max_length=255, blank=True)
    overview = models.TextField(blank=True)
    poster_path = models.CharField(max_length=255, blank=True)
    backdrop_path = models.CharField(max_length=255, blank=True)
    release_date = models.DateField(null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True, help_text="Dakika cinsinden")
    vote_average = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True
    )
    genres = models.ManyToManyField(Genre, related_name='movies', blank=True)

    fetched_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['tmdb_id', 'media_type'],
                name='unique_tmdb_movie',
            ),
        ]
        indexes = [
            models.Index(fields=['tmdb_id', 'media_type']),
            models.Index(fields=['title']),
        ]
        ordering = ['-release_date']

    def __str__(self):
        year = self.release_date.year if self.release_date else 'N/A'
        return f"{self.title} ({year})"

    @property
    def poster_url(self):
        """TMDB'nin tam poster URL'i. Template'te {{ movie.poster_url }} ile kullanılır."""
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/w500{self.poster_path}"
        return None

    @property
    def release_year(self):
        return self.release_date.year if self.release_date else None