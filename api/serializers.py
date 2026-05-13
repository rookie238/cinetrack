"""DRF serializers — model'leri JSON'a çeviren katman."""
from rest_framework import serializers

from movies.models import Genre, Movie
from tracking.models import Review, WatchEntry


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'tmdb_id', 'name']


class MovieSerializer(serializers.ModelSerializer):
    """Film/dizi serializer'ı. Nested genres + computed poster_url."""
    genres = GenreSerializer(many=True, read_only=True)
    poster_url = serializers.ReadOnlyField()
    release_year = serializers.ReadOnlyField()

    class Meta:
        model = Movie
        fields = [
            'id', 'tmdb_id', 'media_type', 'title', 'original_title',
            'overview', 'release_date', 'release_year',
            'runtime', 'vote_average', 'poster_path', 'poster_url',
            'genres',
        ]


class WatchEntrySerializer(serializers.ModelSerializer):
    """WatchEntry serializer. Okumada user + nested movie, yazmada movie_id."""
    user = serializers.StringRelatedField(read_only=True)
    movie = MovieSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(), source='movie', write_only=True,
    )

    class Meta:
        model = WatchEntry
        fields = ['id', 'user', 'movie', 'movie_id', 'status', 'rating', 'added_at', 'updated_at']
        read_only_fields = ['added_at', 'updated_at']


class ReviewSerializer(serializers.ModelSerializer):
    """Review serializer. Like + comment count computed field'ları dahil."""
    user = serializers.StringRelatedField(read_only=True)
    movie = MovieSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(), source='movie', write_only=True,
    )
    like_count = serializers.ReadOnlyField()
    comment_count = serializers.ReadOnlyField()

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'movie', 'movie_id', 'rating', 'text',
            'created_at', 'updated_at', 'like_count', 'comment_count',
        ]
        read_only_fields = ['created_at', 'updated_at']
