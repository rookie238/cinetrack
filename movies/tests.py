"""Movies app tests — Movie model + search/detail view'lar."""
from datetime import date

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from movies.models import Genre, Movie


class MovieModelTest(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(tmdb_id=28, name='Action')
        self.movie = Movie.objects.create(
            tmdb_id=27205, media_type='movie',
            title='Inception', original_title='Inception',
            release_date=date(2010, 7, 16), vote_average=8.4,
        )
        self.movie.genres.add(self.genre)

    def test_movie_str(self):
        self.assertEqual(str(self.movie), 'Inception (2010)')

    def test_poster_url_with_path(self):
        self.movie.poster_path = '/abc.jpg'
        self.assertEqual(
            self.movie.poster_url,
            'https://image.tmdb.org/t/p/w500/abc.jpg',
        )

    def test_poster_url_empty(self):
        self.assertIsNone(self.movie.poster_url)

    def test_unique_tmdb_id_per_media_type(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Movie.objects.create(
                    tmdb_id=27205, media_type='movie',
                    title='Duplicate', original_title='Duplicate',
                )


class SearchViewTest(TestCase):
    def test_empty_search_renders_page(self):
        response = self.client.get(reverse('movies:search'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ara')


class MovieDetailViewTest(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            tmdb_id=99999, media_type='movie',
            title='Test Movie', original_title='Test Movie',
        )

    def test_valid_detail_loads(self):
        url = reverse('movies:detail', kwargs={'media_type': 'movie', 'tmdb_id': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Movie')

    def test_invalid_media_type_returns_404(self):
        response = self.client.get('/movies/invalid/99999/')
        self.assertEqual(response.status_code, 404)
