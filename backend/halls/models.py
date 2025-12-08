from django.db import models


class Hall(models.Model):
    """
    Зал (Context).
    Містить корінь структури компонентів.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class HallComponent(models.Model):
    """
    Component (Abstract/Base).
    Це вузол нашого дерева Composite.
    """
    # Зв'язок з залом
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='all_components')

    # Зв'язок для побудови дерева (Parent -> Children)
    # Якщо parent == null, це кореневий елемент
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')

    name = models.CharField(max_length=100, blank=True)  # Назва ряду або сектора

    def get_details(self):
        """Метод, який вимагає патерн Composite"""
        return f"Component: {self.name}"

    def get_price_modifier(self):
        """Базовий модифікатор ціни"""
        return 1.0

    def __str__(self):
        return f"{self.name} (Hall: {self.hall.name})"


class SeatGroup(HallComponent):
    """
    Composite (Container).
    Наприклад: "Сектор А", "Ряд 1".
    Може містити інші SeatGroup або Seat (через parent field у дітей).
    """
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Seat Group (Row/Sector)"


class Seat(HallComponent):
    """
    Leaf (Лист).
    Конкретне місце.
    """
    number = models.IntegerField()
    is_vip = models.BooleanField(default=False)

    def get_details(self):
        type_str = "VIP" if self.is_vip else "Standard"
        return f"Seat {self.number} ({type_str})"

    def get_price_modifier(self):
        # VIP місця дорожчі на 50%
        return 1.5 if self.is_vip else 1.0

    class Meta:
        verbose_name = "Seat"
