"""Accounts views — auth + profile."""
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render

from tracking.models import Review, WatchEntry

from .forms import ProfileUpdateForm, SignUpForm
from .models import Profile

User = get_user_model()


def signup_view(request):
    """Yeni kullanıcı kaydı."""
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
    """Kendi profiline yönlendir."""
    return redirect('accounts:profile_detail', username=request.user.username)


def profile_detail_view(request, username):
    """Kullanıcının profili: stats + watch lists + reviews."""
    user_obj = get_object_or_404(
        User.objects.select_related('profile'),
        username=username,
    )
    is_self = request.user.is_authenticated and request.user == user_obj

    # Eski kullanıcıların eksik profile'ını otomatik yarat (güvenlik ağı)
    profile_obj, _ = Profile.objects.get_or_create(user=user_obj)

    # Watch entries — status'a göre ayır
    watch_entries = (
        WatchEntry.objects
        .filter(user=user_obj)
        .select_related('movie')
        .prefetch_related('movie__genres')
        .order_by('-updated_at')
    )
    watched = [e for e in watch_entries if e.status == WatchEntry.Status.WATCHED]
    watching = [e for e in watch_entries if e.status == WatchEntry.Status.WATCHING]
    want = [e for e in watch_entries if e.status == WatchEntry.Status.WANT]

    # Reviews
    reviews = list(
        Review.objects
        .filter(user=user_obj)
        .select_related('movie')
        .order_by('-created_at')
    )

    # Stats — DB'de aggregate
    stats = WatchEntry.objects.filter(
        user=user_obj,
        status=WatchEntry.Status.WATCHED,
    ).aggregate(
        avg_rating=Avg('rating'),
        rated_count=Count('rating'),
    )

    context = {
        'profile_user': user_obj,
        'profile': profile_obj,
        'is_self': is_self,
        'watched': watched,
        'watching': watching,
        'want': want,
        'reviews': reviews,
        'watched_count': len(watched),
        'watching_count': len(watching),
        'want_count': len(want),
        'review_count': len(reviews),
        'avg_rating': stats['avg_rating'],
    }
    return render(request, 'accounts/profile_detail.html', context)


@login_required
def profile_edit_view(request):
    """Profil düzenleme."""
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
