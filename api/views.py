"""DRF ViewSets — Movie, WatchEntry, Review için CRUD endpoint'leri."""
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from movies.models import Movie
from tracking.models import Review, WatchEntry

from .permissions import IsOwnerOrReadOnly
from .serializers import MovieSerializer, ReviewSerializer, WatchEntrySerializer


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """Film/dizi okuma. DB'deki kayıtları listele, ara, sırala."""
    queryset = Movie.objects.prefetch_related('genres').all()
    serializer_class = MovieSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'original_title']
    ordering_fields = ['title', 'release_date', 'vote_average']
    ordering = ['-release_date']
    permission_classes = [IsAuthenticatedOrReadOnly]


class WatchEntryViewSet(viewsets.ModelViewSet):
    """Kullanıcının izleme listesi CRUD'u (sadece kendi entry'leri)."""
    serializer_class = WatchEntrySerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['updated_at', 'rating']
    ordering = ['-updated_at']

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return WatchEntry.objects.none()
        qs = (
            WatchEntry.objects
            .filter(user=self.request.user)
            .select_related('movie')
            .prefetch_related('movie__genres')
        )
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    """Yorum CRUD. Herkes listede görür, sadece sahibi düzenler/siler."""
    queryset = Review.objects.select_related('user', 'movie').prefetch_related('movie__genres').all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        movie_id = self.request.query_params.get('movie')
        if movie_id:
            qs = qs.filter(movie_id=movie_id)
        user_param = self.request.query_params.get('user')
        if user_param:
            qs = qs.filter(user__username=user_param)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
