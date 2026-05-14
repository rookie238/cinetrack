"""DRF API tests — endpoint'ler + authentication + authorization."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from movies.models import Movie
from tracking.models import Review

User = get_user_model()


class MovieAPITest(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            tmdb_id=1, media_type='movie', title='Test', original_title='Test',
        )

    def test_list_movies(self):
        client = APIClient()
        response = client.get('/api/movies/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_retrieve_movie(self):
        client = APIClient()
        response = client.get(f'/api/movies/{self.movie.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Test')


class ReviewAPIAuthTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u', password='pass12345')
        self.movie = Movie.objects.create(
            tmdb_id=1, media_type='movie', title='Test', original_title='Test',
        )

    def test_anonymous_can_list_reviews(self):
        client = APIClient()
        response = client.get('/api/reviews/')
        self.assertEqual(response.status_code, 200)

    def test_anonymous_cannot_create_review(self):
        client = APIClient()
        response = client.post('/api/reviews/', {
            'movie_id': self.movie.id, 'rating': 8, 'text': 'Test'
        })
        self.assertIn(response.status_code, [401, 403])

    def test_authenticated_can_create_review(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post('/api/reviews/', {
            'movie_id': self.movie.id, 'rating': 8, 'text': 'Test review'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Review.objects.count(), 1)
