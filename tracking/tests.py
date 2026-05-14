"""Tracking app tests — WatchEntry, Review, ReviewLike CRUD + authorization."""
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from movies.models import Movie
from tracking.models import Review, WatchEntry

User = get_user_model()


class WatchEntryConstraintTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u', password='pass12345')
        self.movie = Movie.objects.create(
            tmdb_id=1, media_type='movie', title='Test', original_title='Test',
        )

    def test_unique_user_movie_constraint(self):
        WatchEntry.objects.create(user=self.user, movie=self.movie, status='want')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                WatchEntry.objects.create(user=self.user, movie=self.movie, status='watched')


class WatchEntryViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u', password='pass12345')
        self.movie = Movie.objects.create(
            tmdb_id=1, media_type='movie', title='Test', original_title='Test',
        )
        self.url = reverse('tracking:watch_update',
                           kwargs={'media_type': 'movie', 'tmdb_id': 1})

    def test_requires_login(self):
        response = self.client.post(self.url, {'status': 'watched', 'rating': 8})
        self.assertEqual(response.status_code, 302)

    def test_create_watch_entry(self):
        self.client.login(username='u', password='pass12345')
        response = self.client.post(self.url, {'status': 'watched', 'rating': 8})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(WatchEntry.objects.filter(user=self.user, movie=self.movie).exists())

    def test_update_existing_watch_entry(self):
        self.client.login(username='u', password='pass12345')
        WatchEntry.objects.create(user=self.user, movie=self.movie, status='want')
        self.client.post(self.url, {'status': 'watched', 'rating': 9})
        entry = WatchEntry.objects.get(user=self.user, movie=self.movie)
        self.assertEqual(entry.status, 'watched')
        self.assertEqual(entry.rating, 9)


class ReviewLikeAjaxTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u', password='pass12345')
        self.other = User.objects.create_user(username='other', password='pass12345')
        self.movie = Movie.objects.create(
            tmdb_id=1, media_type='movie', title='Test', original_title='Test',
        )
        self.review = Review.objects.create(
            user=self.other, movie=self.movie, rating=8, text='Iyi film'
        )

    def test_like_toggle(self):
        self.client.login(username='u', password='pass12345')
        url = reverse('tracking:review_like', kwargs={'review_id': self.review.id})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['liked'])
        self.assertEqual(data['count'], 1)

        response = self.client.post(url)
        data = response.json()
        self.assertFalse(data['liked'])
        self.assertEqual(data['count'], 0)


class ReviewOwnershipTest(TestCase):
    """Authorization: başkasının yorumunu silemez."""

    def setUp(self):
        self.user1 = User.objects.create_user(username='u1', password='pass12345')
        self.user2 = User.objects.create_user(username='u2', password='pass12345')
        self.movie = Movie.objects.create(
            tmdb_id=1, media_type='movie', title='Test', original_title='Test',
        )
        self.review = Review.objects.create(
            user=self.user1, movie=self.movie, rating=8, text='Iyi'
        )

    def test_cannot_delete_others_review(self):
        self.client.login(username='u2', password='pass12345')
        url = reverse('tracking:review_delete', kwargs={'review_id': self.review.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Review.objects.filter(id=self.review.id).exists())
