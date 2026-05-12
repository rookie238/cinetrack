from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .forms import SignUpForm, ProfileUpdateForm

User = get_user_model()


def signup_view(request):
    """Yeni kullanıcı kaydı. Başarılıysa otomatik giriş yapıp profile'a yönlendir."""
    if request.user.is_authenticated:
        return redirect('accounts:profile_self')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # otomatik giriş
            messages.success(request, f"Hoş geldin {user.username}! Hesabın oluşturuldu.")
            return redirect('accounts:profile_self')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
def profile_self_view(request):
    """Mevcut kullanıcının kendi profili."""
    return redirect('accounts:profile_detail', username=request.user.username)


def profile_detail_view(request, username):
    """Bir kullanıcının profili (kendisi ya da başkası olabilir)."""
    user_obj = get_object_or_404(User.objects.select_related('profile'), username=username)
    is_self = request.user.is_authenticated and request.user == user_obj
    
    # İleride buraya: kullanıcının watch_entries, reviews vb. eklenecek
    context = {
        'profile_user': user_obj,
        'profile': user_obj.profile,
        'is_self': is_self,
    }
    return render(request, 'accounts/profile_detail.html', context)


@login_required
def profile_edit_view(request):
    """Profil düzenleme."""
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil güncellendi.")
            return redirect('accounts:profile_self')
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'accounts/profile_edit.html', {'form': form})