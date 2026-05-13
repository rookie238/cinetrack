"""TMDB'den tüm türleri çekip DB'ye yaz: python manage.py seed_genres"""
from django.core.management.base import BaseCommand

from movies.models import Genre
from movies.services import save_genres_from_tmdb


class Command(BaseCommand):
    help = "TMDB'den tüm film/dizi türlerini çek ve DB'ye kaydet"

    def handle(self, *args, **options):
        self.stdout.write("TMDB'den türler çekiliyor...")
        count = save_genres_from_tmdb()
        total = Genre.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"✓ {count} tür işlendi. DB'de toplam {total} tür var."
        ))
