"""Accounts views — auth + profile + AJAX follow."""
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from tracking.models import Review, WatchEntry

from .forms import ProfileUpdateForm, SignUpForm
from .models import Follow, Profile

User = get_user_model()


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile_self')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Hoş geldin {user.username}!")
            return redirect('accounts:profile_self')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def profile_self_view(request):
    return redirect('accounts:profile_detail', username=request.user.username)


def profile_detail_view(request, username):
    user_obj = get_object_or_404(User.objects.select_related('profile'), username=username)
    is_self = request.user.is_authenticated and request.user == user_obj
    profile_obj, _ = Profile.objects.get_or_create(user=user_obj)

    is_following = False
    if request.user.is_authenticated and not is_self:
        is_following = Follow.objects.filter(
            follower=request.user, following=user_obj
        ).exists()

    watch_entries = (
        WatchEntry.objects.filter(user=user_obj)
        .select_related('movie').prefetch_related('movie__genres')
        .order_by('-updated_at')
    )
    watched = [e for e in watch_entries if e.status == WatchEntry.Status.WATCHED]
    watching = [e for e in watch_entries if e.status == WatchEntry.Status.WATCHING]
    want = [e for e in watch_entries if e.status == WatchEntry.Status.WANT]

    reviews = list(
        Review.objects.filter(user=user_obj).select_related('movie').order_by('-created_at')
    )

    stats = WatchEntry.objects.filter(
        user=user_obj, status=WatchEntry.Status.WATCHED,
    ).aggregate(avg_rating=Avg('rating'), rated_count=Count('rating'))

    return render(request, 'accounts/profile_detail.html', {
        'profile_user': user_obj,
        'profile': profile_obj,
        'is_self': is_self,
        'is_following': is_following,
        'watched': watched,
        'watching': watching,
        'want': want,
        'reviews': reviews,
        'watched_count': len(watched),
        'watching_count': len(watching),
        'want_count': len(want),
        'review_count': len(reviews),
        'avg_rating': stats['avg_rating'],
    })


@login_required
def profile_edit_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil güncellendi.")
            return redirect('accounts:profile_self')
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
@require_POST
def toggle_follow_view(request, username):
    """AJAX: kullanıcıyı takip et / takipten çık. JSON döndürür."""
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return JsonResponse({'error': 'Kendini takip edemezsin'}, status=400)
    follow, created = Follow.objects.get_or_create(
        follower=request.user, following=target,
    )
    if not created:
        follow.delete()
        following = False
    else:
        following = True
    return JsonResponse({
        'following': following,
        'follower_count': target.followers.count(),
    })
