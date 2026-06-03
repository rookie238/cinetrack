"""WatchEntry ve Review için form'lar."""
from django import forms
from .models import Review, WatchEntry


class WatchEntryForm(forms.ModelForm):
    """İzleme durumu ve puan formu."""
    class Meta:
        model = WatchEntry
        fields = ['status', 'rating']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 1, 'max': 10,
                'placeholder': '1-10 (optional)'
            }),
        }
        labels = {
            'status': 'Status',
            'rating': 'Rating',
        }


class ReviewForm(forms.ModelForm):
    """Yorum (review) formu."""
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 1, 'max': 10, 'required': True,
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'What do you think about this movie/series?',
                'required': True,
            }),
        }
        labels = {
            'rating': 'Rating (1-10)',
            'text': 'Review',
        }
