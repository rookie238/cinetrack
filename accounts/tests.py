"""Accounts app tests — signal, follow, signup, AJAX."""
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from accounts.models import Follow, Profile

User = get_user_model()


class ProfileSignalTest(TestCase):
    

    def test_profile_created_on_user_creation(self):
        user = User.objects.create_user(username='test1', password='pass12345')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, Profile)

    def test_profile_not_duplicated_on_save(self):
        user = User.objects.create_user(username='test1', password='pass12345')
        user.first_name = 'Test'
        user.save()
        self.assertEqual(Profile.objects.filter(user=user).count(), 1)


class FollowConstraintsTest(TestCase):
   

    def setUp(self):
        self.user1 = User.objects.create_user(username='u1', password='pass12345')
        self.user2 = User.objects.create_user(username='u2', password='pass12345')

    def test_can_follow_other_user(self):
        Follow.objects.create(follower=self.user1, following=self.user2)
        self.assertEqual(Follow.objects.count(), 1)

    def test_cannot_follow_self(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Follow.objects.create(follower=self.user1, following=self.user1)

    def test_cannot_double_follow(self):
        Follow.objects.create(follower=self.user1, following=self.user2)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Follow.objects.create(follower=self.user1, following=self.user2)


class SignupViewTest(TestCase):
    

    def test_signup_get_returns_form(self):
        response = self.client.get(reverse('accounts:signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Kayıt Ol')

    def test_signup_post_creates_user(self):
        response = self.client.post(reverse('accounts:signup'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())


class FollowAjaxTest(TestCase):
    

    def setUp(self):
        self.user1 = User.objects.create_user(username='u1', password='pass12345')
        self.user2 = User.objects.create_user(username='u2', password='pass12345')

    def test_follow_requires_login(self):
        response = self.client.post(
            reverse('accounts:follow_toggle', kwargs={'username': 'u2'})
        )
        self.assertEqual(response.status_code, 302)

    def test_follow_toggle(self):
        self.client.login(username='u1', password='pass12345')
        url = reverse('accounts:follow_toggle', kwargs={'username': 'u2'})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['following'])
        self.assertEqual(data['follower_count'], 1)

        response = self.client.post(url)
        data = response.json()
        self.assertFalse(data['following'])
        self.assertEqual(data['follower_count'], 0)
