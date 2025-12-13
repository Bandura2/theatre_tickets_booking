from rest_framework import serializers
from .models import Movie, Session


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    hall_name = serializers.CharField(source='hall.name', read_only=True)

    # === ДОДАЄМО ПОЛЕ ДЛЯ ПОСТЕРА ===
    movie_poster = serializers.ImageField(source='movie.poster', read_only=True)

    # ================================

    class Meta:
        model = Session
        # Додайте movie_poster у список полів
        fields = ['id', 'movie', 'movie_title', 'movie_poster', 'hall', 'hall_name', 'start_time', 'price_base']
