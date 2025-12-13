# backend/bookings/serializers.py
from rest_framework import serializers
from .models import Booking, Ticket


class TicketSerializer(serializers.ModelSerializer):
    seat_number = serializers.IntegerField(source='seat.number', read_only=True)

    # Дані про сеанс
    movie_title = serializers.CharField(source='session.movie.title', read_only=True)
    hall_name = serializers.CharField(source='session.hall.name', read_only=True)
    start_time = serializers.DateTimeField(source='session.start_time', read_only=True)

    # === ВИПРАВЛЕННЯ: замість is_vip пишемо seat_type ===
    seat_type = serializers.CharField(source='seat.seat_type', read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'seat', 'seat_number', 'status', 'price',
            'movie_title', 'hall_name', 'start_time', 'seat_type'
        ]


class BookingSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'user', 'created_at', 'total_price', 'discount_applied', 'tickets']
