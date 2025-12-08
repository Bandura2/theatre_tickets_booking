from rest_framework import serializers
from .models import Booking, Ticket


class TicketSerializer(serializers.ModelSerializer):
    seat_number = serializers.IntegerField(source='seat.number', read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'seat', 'seat_number', 'status', 'price']


class BookingSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'user', 'created_at', 'total_price', 'discount_applied', 'tickets']
