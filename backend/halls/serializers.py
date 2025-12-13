# backend/halls/serializers.py
from rest_framework import serializers
from .models import Hall, HallComponent, Seat


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        # === ВИПРАВЛЕННЯ: замість is_vip пишемо seat_type ===
        fields = ['id', 'number', 'seat_type']


class HallComponentSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    seat_details = serializers.SerializerMethodField()

    class Meta:
        model = HallComponent
        fields = ['id', 'name', 'type', 'children', 'seat_details']

    def get_children(self, obj):
        return HallComponentSerializer(obj.children.all(), many=True).data

    def get_type(self, obj):
        # Визначаємо, чи це компонент-група чи місце
        return 'seat' if hasattr(obj, 'seat') else 'group'

    def get_seat_details(self, obj):
        # Якщо це місце, серіалізуємо його деталі
        return SeatSerializer(obj.seat).data if hasattr(obj, 'seat') else None


class HallSerializer(serializers.ModelSerializer):
    structure = serializers.SerializerMethodField()

    class Meta:
        model = Hall
        fields = ['id', 'name', 'structure']

    def get_structure(self, obj):
        return HallComponentSerializer(obj.all_components.filter(parent=None), many=True).data
