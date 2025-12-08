from rest_framework import serializers
from .models import Hall, HallComponent, Seat


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id', 'number', 'is_vip']


class HallComponentSerializer(serializers.ModelSerializer):
    # Рекурсивне поле: компонент може мати дітей (інші компоненти)
    children = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    seat_details = serializers.SerializerMethodField()

    class Meta:
        model = HallComponent
        fields = ['id', 'name', 'type', 'children', 'seat_details']

    def get_children(self, obj):
        # Шукаємо всіх дітей цього компонента
        children = obj.children.all()
        return HallComponentSerializer(children, many=True).data

    def get_type(self, obj):
        # Визначаємо, чи це Ряд (Group) чи Місце (Seat)
        if hasattr(obj, 'seat'):
            return 'seat'
        return 'group'

    def get_seat_details(self, obj):
        # Якщо це місце, додаємо деталі
        if hasattr(obj, 'seat'):
            return SeatSerializer(obj.seat).data
        return None


class HallSerializer(serializers.ModelSerializer):
    # Повертаємо тільки кореневі компоненти (у яких parent=None)
    structure = serializers.SerializerMethodField()

    class Meta:
        model = Hall
        fields = ['id', 'name', 'description', 'structure']

    def get_structure(self, obj):
        root_components = obj.all_components.filter(parent=None)
        return HallComponentSerializer(root_components, many=True).data
