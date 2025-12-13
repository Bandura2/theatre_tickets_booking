from rest_framework import serializers
from .models import Movie, Session


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    hall_name = serializers.CharField(source='hall.name', read_only=True)
    genre = serializers.CharField(source='movie.genre', read_only=True)
    movie_poster = serializers.ImageField(source='movie.poster', read_only=True)
    description = serializers.CharField(source='movie.description', read_only=True)

    class Meta:
        model = Session
        fields = [
            'id', 'movie', 'movie_title', 'movie_poster',
            'genre', 'description',  # <--- ТУТ
            'hall', 'hall_name', 'start_time', 'price_base'
        ]
